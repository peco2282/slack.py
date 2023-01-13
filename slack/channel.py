from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .route import Route
from .base import Sendable
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
        self.team: Optional[Team] = self.state.teams.get(data.get("context_team_id", ""))
        self.created_at: datetime = datetime.fromtimestamp(float(data.get("created", 0)))
        self.created_by: Optional[Member] = self.state.members.get(data.get("creator"))
        # self.overload(data)

    async def kick(self, member: Member):
        """
        Removes a user from a conversation.

        Parameters
        ----------
        member: `Member`

        Returns
        -------

        """
        query = {
            "user": member.id,
            "channel": self.id
        }
        return await self.http.post_anything(
            Route("POST", "conversations.kick", self.http.bot_token),
            query=query
        )

    async def leave(self, member: Member):
        query = {
            "user": member.id,
            "channel": self.id
        }
        return await self.http.manage_channel(
            Route("POST", "conversations.leave", self.http.bot_token),
            query=query
        )

    async def members(self):
        return await self.http.get_anything(
            Route("GET", "conversations.members", self.http.bot_token)
        )

    async def unarchive(self):
        param = {
            "channel": self.id
        }
        rtn = await self.state.http.request(
            Route("POST", "channels.unarchive", self.state.http.bot_token),
            data=param
        )
        return rtn

    async def replies(self):
        rtn = await self.state.http.send_message(
            Route("GET", "conversations.replies", self.state.http.bot_token)
        )
        return rtn

    async def edit(
            self,
            title: str = None,
            purpose: str = None,
    ):
        pass


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
