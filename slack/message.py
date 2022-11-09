from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .route import Route
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

    id : :class:`str`
        Message ID.

    content: :class:`str`
        Message content.

    created_at: :class:`datetime`
        Message created at.

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
        """
        Returns
        -------
        :class:`~Channel`
            Message channel.

        """
        return self.state.channels[self.channel_id]

    @property
    def author(self) -> Member:
        """
        Returns
        -------
        :class:`~Member`
            Message author.

        """
        return self.state.members[self.user]

    @property
    def team(self) -> Team:
        """
        Returns
        -------
        :class:`~Team`
            Message team.

        """
        return self.state.teams[self.team_id]

    async def delete(self) -> None:
        """It deletes a message.
        """
        param = {
            "channel": self.channel_id,
            "ts": self.id,
        }
        self.state.http.delete_message(
            Route(
                "DELETE",
                "message.delete",
                self.state.http.bot_token
            ),
            param
        )


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


class PurposeMessage(JoinMessage):
    """This function is a constructor for the class PurposeMessage

    Attributes
    ----------
    purpose : :class:`str`
        The purpose of channel.

    """
    def __init__(self, state: ConnectionState, data: PurposeMessagePayload):
        super().__init__(state, data)
        self.purpose = data.get("purpose")


class PreviousMessage:
    """
    Attributes
    ----------
    text: str
        Message

    user: Member
        Sent by

    team: Team
        Sent team

    ts: datetime
        timestamp
    """
    def __init__(self, state: ConnectionState, data: PreviousMessagePayload):
        self.state = state
        self.client_msg_id = data.get("client_msg_id")
        self.text = data.get("text")
        self.user = self.state.members[data.get("user")]
        self.team = self.state.teams[data.get("team")]
        self.ts = datetime.fromtimestamp(float(data.get("ts")))


class DeletedMessage:
    """This function is used to delete a message from a channel

    Attributes
    ----------
    channel : :class:`Channel`
        The deleted Message.

    ts: :class:`datetime`
        time when deleted

    hidden: :class:`bool`
        is ephemeral

    deleted_text: :class:`str`
        The text what deleted message.

    """
    def __init__(self, state: ConnectionState, data: DeletedMessagePayload):
        self.state = state
        self.channel: Channel = self.state.channels[data.get("channel")]
        self.ts: datetime = datetime.fromtimestamp(float(data.get("ts")))
        self.previous_message: PreviousMessage = PreviousMessage(self.state, data.get("previous_message"))
        self.hidden: bool = data.get("hidden")
        self.deleted_text: str = self.previous_message.text


class ArchivedMessage:
    """A constructor for the class.

    Attributes
    ----------
    ts : :class:`datetime`
        The data that was sent in the message.

    user: :class:`Member`
        The user who archibed channel

    channel: :class:`Channel`
        Archived channel.

    """
    def __init__(self, state: ConnectionState, data: ArchivedMessagePayload):
        self.state = state
        self.ts = data.get("ts")
        self.user: Member = self.state.members[data.get("user")]
        self.channel: Channel = self.state.channels[data.get("channel")]
        # self.channel_type = data.get("channel_type")
