from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .message import Message
from .base import Sendable
from .errors import InvalidArgumentException
from .route import Route
from .team import Team
from .types.channel import (
    Channel as ChannelPayload,
    DeletedChannel as DeletedChannelPayload
)

if TYPE_CHECKING:
    from .state import ConnectionState
    from .member import Member

__all__ = (
    "Channel",
    "DeletedChannel"
)


# > A `Channel` is a named pipe that can be used to send and receive messages
class Channel(Sendable):
    """This function is a constructor for the Channel class. It takes in a ConnectionState object and a ChannelPayload
    object. It sets the state, id, name, team, created_at, and created_by attributes of the Channel object. It then
    calls the overload function

    Attributes
    ----------
    id : :class:`str`
        Channel ID.

    team : :class:`Team`
        Your team object.

    name: :class:`str`
        Account name.

    created_at: :class:`datetime`
        When create this channel.

    created_by: :class:`Member`
        Who channel create.

    """

    def __init__(self, state: ConnectionState, data: ChannelPayload):
        self.state = state
        self.http = state.http
        self.id: str = data.get("id")
        self.name = data.get("name")
        self.team: Team | None = self.state.teams.get(data.get("context_team_id", ""))
        self.created_at: datetime = datetime.fromtimestamp(float(data.get("created", 0)))
        self.created_by: Member | None = self.state.members.get(data.get("creator"))
        # self.overload(data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    async def kick(self, member: Member) -> None:
        """
        A way to :class:`Member`.kick()
        Removes a user from a conversation.

        ..versionadded:: 1.4.3

        Parameters
        ----------
        member: `Member`

        """
        if not isinstance(member, Member):
            raise InvalidArgumentException("member parameter must be `Member` class.")

        await member.kick(self)

    async def leave(self, member: Member):
        """
        Leaves a conversation.

        ..versionadded:: 1.4.3

        Parameters
        ----------
        member: :class:`Member`
            Member who leave channel.
        """
        if not isinstance(member, Member):
            raise InvalidArgumentException("member parameter must be `Member` class.")
        query = {
            "user": member.id,
            "channel": self.id
        }
        await self.http.manage_channel(
            Route("POST", "conversations.leave", self.http.bot_token),
            query=query
        )

    async def members(self, channel_id: str | None = None) -> list[Member | None]:
        """
        Return List channel the calling user may access.

        ..versionadded:: 1.4.3


        Parameters
        ----------
        channel_id: Optional[:class:`str`]

        Returns
        -------
        List[Optional[:class:`Member`]]
            Users participating in the channel.
        """
        rtn = await self.http.get_anything(
            Route("GET", "conversations.members", self.http.bot_token),
            query={
                "channel": channel_id or self.id
            }
        )
        members = rtn["members"]
        return [self.state.members[user] for user in members]

    async def unarchive(self) -> None:
        """
        This channel unarchive.

        ..versionadded:: 1.4.3
        """
        param = {
            "channel": self.id
        }
        await self.state.http.request(
            Route("POST", "channels.unarchive", self.state.http.bot_token),
            data=param
        )

    async def edit(
            self,
            name: str = None,
            title: str | None = None,
            purpose: str | None = None,
            topic: str | None = None
    ) -> Channel:
        """It edits the channel's title, purpose, or topic.

        .. versionadded:: 1.4.3

        Parameters
        ----------
        name : Optional[:class:`str`]
            The new name of the channel.
        title : Optional[:class:`str`]
            The new title of the channel.
        purpose : Optional[:class:`str`]
            The purpose of the channel.
        topic : Optional[:class:`str`]
            The channel topic.

        Returns
        -------
        :class:`Channel`
            Edited channel object.
        """
        if not any([q is not None for q in (name, title, purpose, topic)]):
            raise InvalidArgumentException("Some parameter needs to be filled in.")
        ch: dict[str, Any] = {}
        if name is not None:
            ch = await self.http.manage_channel(
                Route("POST", "conversation.rename", self.http.bot_token),
                query={
                    "channel": self.id,
                    "name": str(name)
                }
            )
        if title is not None:
            ch = await self.http.manage_channel(
                Route("POST", "conversations.setTitle", self.http.bot_token),
                query={
                    "channel": self.id,
                    "title": str(title)
                }
            )

        if purpose is not None:
            ch = await self.http.manage_channel(
                Route("POST", "conversations.setPurpose", self.http.bot_token),
                query={
                    "channel": self.id,
                    "title": str(title)
                }
            )
        if topic is not None:
            ch = await self.http.manage_channel(
                Route("POST", "conversations.setTopic", self.http.bot_token),
                query={
                    "channel": self.id,
                    "topic": str(title)
                }
            )

        channel = Channel(self.state, ch["channel"])
        self.state.channels[self.id] = channel
        return channel

    async def reaction_messages(
            self,
            *,
            team: Team | None = None,
            member: Member | None = None
    ) -> list[Message | None]:
        """
        Returns a list of messages that have been reacted to on the specified channel.

        ..versionadded:: 1.4.3

        Parameters
        ----------
        team: Optional[:class:`Team`]
            Team to be sent from.

        member: Optional[:class:`Member`]
            Member to be sent from.

        Returns
        -------

        """
        query = {}
        if team is not None:
            query["team_id"] = team.id

        if member is not None:
            query["member"] = member.id

        rtn = await self.http.manage_channel(
            Route("GET", "reactions.list", self.http.bot_token),
            query=query
        )
        items = rtn["items"]
        messages = []
        for item in items:
            message = Message(self.state, item["message"])
            message.channel_id = item["channel"]
            messages.append(message)

        return messages


class DeletedChannel:
    """This function is called when a channel is deleted

    Attributes
    ----------
    channel_id : :class:`str`
        deleted channel id.

    """

    def __init__(self, state: ConnectionState, data: DeletedChannelPayload):
        self.state = state
        self.channel_id: str = data.get("channel")
        self.deleted_at: datetime = datetime.fromtimestamp(float(data.get("event_ts", "nan")))
