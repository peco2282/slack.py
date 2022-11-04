from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING


from .member import Member

if TYPE_CHECKING:
    from .team import Team
    from .state import ConnectionState
    from .channel import Channel

from .types.message import (
    Message as MessagePayload,
    JoinMessage as JoinMessagePayload,
    PurposeMessage as PurposeMessagePayload,
    PreviousMessage as PreviousMessagePayload,
    DeletedMessage as DeletedMessagePayload,
    ArchivedMessage as ArchivedMessagePayload
)

__all__ = (
    "Message",
    "JoinMessage",
    "PurposeMessage",
    "DeletedMessage",
    "ArchivedMessage"
)


class Message:
    """This function is a constructor for the Message class. It takes in two parameters, state and data. The state
    parameter is a ConnectionState object, and the data parameter is a MessagePayload object. The function then sets the
    state, team_id, id, author, channel_id, and created_at attributes of the Message object

    Attributes
    ----------
    state : :class:`ConnectionState`
        The connection state.

    id : :class:`str`
        Channel ID.

    team_id : :class:`str`
        Your team ID.

    user: :class:`str`
        Account name.

    """
    def __init__(self, state: ConnectionState, data: MessagePayload):
        self.state = state
        self.team_id = data.get("team")
        self.id = data.get("ts")
        self.user = data.get("user")
        self.channel_id = data.get("channel")
        self.content = data.get("text", "")
        self.created_at: datetime = datetime.fromtimestamp(float(self.id))

    @property
    def channel(self) -> Channel:
        return self.state.channels[self.channel_id]

    @property
    def author(self) -> Member:
        return self.state.members[self.user]

    @property
    def team(self) -> Team:
        return self.state.teams[self.team_id]

    async def delete(self, text: str, ts: str = None) -> None:
        """It deletes a message.

        Parameters
        ----------
        text : str
            The text of the message to send.
        ts : str
            The timestamp of the message to be deleted.

        """
        param = {
            "channel": self.channel_id,
            "ts": ts or self.id,
            "text": text
        }
        self.state.http.delete_message(param)


class JoinMessage(Message):
    """This function is a constructor for the JoinMessage class. It takes in a ConnectionState and a JoinMessagePayload as
    parameters and sets the author of the message to the user in the JoinMessagePayload

    Attributes
    ----------
    state : :class:`ConnectionState`
        The ConnectionState object that represents the current state of the connection.

    """
    def __init__(self, state: ConnectionState, data: JoinMessagePayload):
        super().__init__(state, data)
        self.state = state


class PurposeMessage(JoinMessage):
    """This function is a constructor for the class PurposeMessage

    Attributes
    ----------
    state : :class:`ConnectionState`
        The ConnectionState object that is passed to the ConnectionState.handle_message() method.

    """
    def __init__(self, state: ConnectionState, data: PurposeMessagePayload):
        super().__init__(state, data)
        self.state = state


class PreviousMessage:
    def __init__(self, state: ConnectionState, data: PreviousMessagePayload):
        self.state = state
        self.client_msg_id = data.get("client_msg_id")
        self.text = data.get("text")
        self.user = self.state.members[data.get("user")]
        self.team = self.state.teams[data.get("team")]
        self.ts = data.get("ts")


class DeletedMessage:
    """This function is used to delete a message from a channel

    Attributes
    ----------
    state : ConnectionState
        The ConnectionState object that contains information about the connection.

    channel : Channel
        The deleted Message.

    ts: str
        time when deleted

    deleted_text: str
        The text what deleted message.

    """
    def __init__(self, state: ConnectionState, data: DeletedMessagePayload):
        self.state = state
        self.channel = self.state.channels[data.get("channel")]
        self.ts = data.get("ts")
        self.previous_message = PreviousMessage(self.state, data.get("previous_message"))
        self.hidden = data.get("hidden")
        self.deleted_text = self.previous_message.text


class ArchivedMessage:
    """A constructor for the class.

    Attributes
    ----------
    state : ConnectionState
        ConnectionState

    ts : str
        The data that was sent in the message.

    user: Member
        The user who archibed channel

    channel: Channel
        Archived channel.

    """
    def __init__(self, state: ConnectionState, data: ArchivedMessagePayload):
        self.state = state
        self.__data = data
        self.ts = data.get("ts")
        self.user = data.get("user")
        self.channel = self.state.channels[data.get("channel")]
        self.channel_type = data.get("channel_type")
