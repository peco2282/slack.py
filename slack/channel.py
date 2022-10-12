from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .types.channel import (
    Channel as ChannelPayload,
    DeletedChannel as DeletedChannelPayload
)

if TYPE_CHECKING:
    from .state import ConnectionState
    from .route import Route
    from .message import Message

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
    state : :class:`ConnectionState`
        The connection state.

    id : :class:`str`
        Channel ID.

    team : :class:`Team`
        Your team object.

    name: :class:`str`
        Account name.

    created_at: :class:`datetime`
        When create this channel.

    created_by: :class:`str`
        Who channel create.

    """
    def __init__(self, state: ConnectionState, data: ChannelPayload):
        self.state = state
        self.id: str = data.get("id")
        self.name = data.get("name")
        self.team: str = data.get("context_team_id")
        self.created_at: datetime = datetime.fromtimestamp(float(data.get("created", 0)))
        self.created_by: str = data.get("creator")
        self.overload(data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    def overload(self, data: ChannelPayload):
        pass

    async def send(self, text: str) -> Message:
        """It sends a message to a channel.

        Parameters
        ----------
        text : str
            The text of the message to send.

        Returns
        -------
            A Message object.

        """
        param = {
            "channel": self.id,
            "text": text
        }
        message = await self.state.http.send_message(
            Route("POST", "chat.postMessage", token=self.state.http.bot_token),
        )
        return Message(state=self.state, data=message["message"])

    async def send_as_user(self, text: str):
        param = {
            "channel": self.id,
            "text": text
        }
        message = await self.state.http.send_message(
            Route(method="POST", endpoint="chat.postMessage", token=self.state.http.user_token)
        )
        return Message(state=self.state, data=message["message"])


class DeletedChannel:
    """This function is called when a channel is deleted

    Attributes
    ----------
    state : :class:`ConnectionState`
        ConnectionState

    """
    def __init__(self, state: ConnectionState, data: DeletedChannelPayload):
        self.state = state
        self.channel = data.get("channel")
        self.ts: datetime = datetime.fromtimestamp(float(data.get("event_ts", "nan")))
