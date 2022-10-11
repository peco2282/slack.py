from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from . import Member

if TYPE_CHECKING:
    from . import (
        Team,
        ConnectionState
    )
from .types import (
    Message as MessagePayload,
    JoinMessage as JoinMessagePayload,
    PurposeMessage as PurposeMessagePayload,
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
    """
    Message l
    """

    def __init__(self, state: ConnectionState, data: MessagePayload):
        """This function is a constructor for the Message class. It takes in two parameters, state and data. The state
        parameter is a ConnectionState object, and the data parameter is a MessagePayload object. The function then sets the
        state, team_id, id, author, channel_id, and created_at attributes of the Message object

        Parameters
        ----------
        state : ConnectionState
            The connection state.
        data : MessagePayload
            The data that was sent to the server.

        """
        self.state = state
        self.team_id = data.get("team")
        self.id = data.get("ts")
        self.user = data.get("user")
        self.channel_id = data.get("channel")
        self.content = data.get("text", "")
        self.created_at: datetime = datetime.fromtimestamp(float(self.id))

    @property
    def channel(self):
        return self.state.channels[self.channel_id]

    @property
    def author(self) -> Member:
        return self.state.members[self.user]

    @property
    def team(self) -> Team:
        return self.state.teams[self.team_id]

    async def delete(self, text: str, ts: str = None):
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
    def __init__(self, state: ConnectionState, data: JoinMessagePayload):
        """This function is a constructor for the JoinMessage class. It takes in a ConnectionState and a JoinMessagePayload as
        parameters and sets the author of the message to the user in the JoinMessagePayload

        Parameters
        ----------
        state : ConnectionState
            The ConnectionState object that represents the current state of the connection.
        data : JoinMessagePayload
            The data that was sent with the event.

        """
        super().__init__(state, data)


class PurposeMessage(JoinMessage):
    def __init__(self, state: ConnectionState, data: PurposeMessagePayload):
        """This function is a constructor for the class PurposeMessage

        Parameters
        ----------
        state : ConnectionState
            The ConnectionState object that is passed to the ConnectionState.handle_message() method.
        data : PurposeMessagePayload
            The data that was sent by the client.

        """
        super().__init__(state, data)
        self.state = state


class DeletedMessage:
    def __init__(self, state: ConnectionState, data: DeletedMessagePayload):
        """This function is used to delete a message from a channel

        Parameters
        ----------
        state : ConnectionState
            The ConnectionState object that contains information about the connection.
        data : DeletedMessagePayload
            The data that was sent by the server.

        """
        self.channel = data.get("channel")


class ArchivedMessage:
    def __init__(self, state: ConnectionState, data: ArchivedMessagePayload):
        """A constructor for the class.

        Parameters
        ----------
        state : ConnectionState
            ConnectionState
        data : ArchivedMessagePayload
            The data that was sent in the message.

        """
        pass
