from __future__ import annotations

import json
import urllib.parse
from datetime import datetime
from typing import TYPE_CHECKING, Optional, overload

from .member import Member
from .message import Message
from .route import Route
from .errors import InvalidParamException
from .team import Team
from .types.channel import (
    Channel as ChannelPayload,
    DeletedChannel as DeletedChannelPayload
)
from .view import ViewFrame

if TYPE_CHECKING:
    from .state import ConnectionState

__all__ = (
    "Channel",
    "DeletedChannel"
)


# > A `Channel` is a named pipe that can be used to send and receive messages
class Channel:
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
        self.id: str = data.get("id")
        self.name = data.get("name")
        self.team: Team = self.state.teams[data.get("context_team_id")]
        self.created_at: datetime = datetime.fromtimestamp(float(data.get("created", 0)))
        self.created_by: Optional[Member] = self.state.members.get(data.get("creator"))
        # self.overload(data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    @overload
    async def send(
            self,
            text: str
    ):
        ...

    @overload
    async def send(
            self,
            view: ViewFrame
    ):
        ...

    async def send(
            self,
            text: str = None,
            view: Optional[ViewFrame] = None
    ) -> Message:
        """|coro|

        It sends a message to a channel.

        Parameters
        ----------
        text : Optional[:class:`str`]
            The text of the message to send.

        view: Optional[:class:`ViewFrame`]
            The viewframe contain blocks of the message to send.

        Returns
        -------
        :class:`Message`
            A Message object.

        """
        param = query = None
        if (text is not None) and (view is not None):
            raise InvalidParamException()

        if text is not None:
            param = {
                "channel": self.id,
                "text": str(text)
            }

        if view is not None:
            blocks = json.dumps(view.to_list())
            query = {
                "channel": self.id,
                "blocks": urllib.parse.quote(str(blocks)).replace("%25", "%").replace("%27", "%22")
            }

        message = await self.state.http.send_message(
            Route("POST", "chat.postMessage", token=self.state.http.bot_token),
            data=param,
            query=query
        )
        msg = Message(state=self.state, data=message["message"])
        msg.channel_id = self.id
        return msg

    async def send_as_user(self, text: str):
        """|coro|

        Parameters
        ----------
        text: :class:`str`
            Message you want to send by your.

        Returns
        -------
        :class:`~Message`
            A Message object.

        """
        param = {
            "channel": self.id,
            "text": text
        }
        message = await self.state.http.send_message(
            Route(method="POST", endpoint="chat.postMessage", token=self.state.http.user_token),
            data=param
        )
        return Message(state=self.state, data=message["message"])

    async def archive(self):
        """
        This channel archive.

        .. versionadded 1.3.0
        """
        param = {
            "channel": self.id
        }
        await self.state.http.create_channel(
            Route("POST", "conversations.archive", token=self.state.http.bot_token),
            param
        )


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
