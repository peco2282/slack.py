from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .route import Route

if TYPE_CHECKING:
    from .team import Team
    from .state import ConnectionState
    from .channel import Channel
    from .member import Member


# noinspection PyProtectedMember
from .types.message import (
    _Edited,
    Message as MessagePayload,
    JoinMessage as JoinMessagePayload,
    PurposeMessage as PurposeMessagePayload,
    PreviousMessage as PreviousMessagePayload,
    DeletedMessage as DeletedMessagePayload
)

__all__ = (
    "Message",
    "JoinMessage",
    "PurposeMessage",
    "DeletedMessage",
)


class Message:
    """This class is a constructor for the Message class. It takes in two parameters, state and data. The state
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
        self.scheduled_message_id: Optional[str] = None
        self.__edited: Optional[_Edited] = data.get("edited")
        self.__edited_ts: str = self.__edited.get("ts") if self.__edited else self.id
        self.__edited_user: Optional[Member] = self.state.members.get(
            self.__edited.get("user")) if self.__edited else None
        self.edited_at = datetime.fromtimestamp(float(self.__edited_ts))

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} channel_id={self.channel_id}>"

    @property
    def channel(self) -> Channel:
        """Message channel data.

        Returns
        -------
        :class:`Channel`
            Message channel.

        """
        return self.state.channels[self.channel_id]

    @property
    def author(self) -> Optional[Member]:
        """Message author.

        Returns
        -------
        Optional[:class:`Member`]
            Message author.

        """
        return self.state.members.get(self.user)

    @property
    def team(self) -> Team:
        """Message team.

        Returns
        -------
        :class:`Team`
            Message team.

        """
        return self.state.teams.get(self.team_id)

    async def edit(self, text: str, is_bot: bool = True):
        """|coro|
        Edit sent message.

        .. versionadded:: 1.4.0

        Parameters
        ----------
        text: :class:`str`
            New message.

        is_bot: :class:`bool`
            If my(Bot) message, True.

        Returns
        -------
        :class:`Message`
            message data with edited timestamp.

        """
        param = {
            "channel": self.channel_id,
            "ts": self.id,
            "text": str(text)
        }
        if is_bot:
            route = Route("POST", "chat.update", self.state.http.bot_token)

        else:
            route = Route("POST", "chat.update", self.state.http.user_token)
        rtn = await self.state.http.send_message(
            route,
            data=param
        )
        return Message(self.state, rtn["message"])

    async def delete(self) -> DeletedMessage:
        """It deletes a message.

        .. versionchanged:: 1.4.0
            Return :class:`DeletedMessage`

        Returns
        -------
        :class:`DeletedMessage`
            A DeletedMessage object.
        """
        param = {
            "channel": self.channel_id,
            "ts": self.id
        }
        rtn = await self.state.http.delete_message(
            Route(
                "DELETE",
                "chat.delete",
                self.state.http.bot_token
            ),
            param
        )
        rtn.pop("ok")
        return DeletedMessage(self.state, rtn)

    async def reply(self, text: str):
        """

        Parameters
        ----------
        text: :class:`str`

        Returns
        -------
        :class:`Message`
        """
        param = {
            "channel": self.channel_id,
            "thread_ts": self.id,
            "text": str(text)
        }
        rtn = await self.state.http.send_message(
            Route("POST", "chat.postMessage", self.state.http.bot_token),
            data=param
        )
        return Message(self.state, rtn["message"])


class JoinMessage(Message):
    """This function is a constructor for the JoinMessage class. It takes in a ConnectionState and a JoinMessagePayload as
    parameters and sets the author of the message to the user in the JoinMessagePayload

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
    text: :class:`str`
        Message

    user: :class:`Member`
        Sent by

    team: :class:`Team`
        Sent team

    ts: :class:`datetime`
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
    ts: :class:`datetime`
        time when deleted.
    """

    def __init__(self, state: ConnectionState, data: DeletedMessagePayload):
        self.__data = data
        self.state = state
        self.ts: datetime = datetime.fromtimestamp(float(data.get("ts")))
        # self.previous_message: PreviousMessage = PreviousMessage(self.state, data.get("previous_message"))
        # self.hidden: bool = data.get("hidden", False)
        # self.deleted_text: str = self.previous_message.text

    @property
    def channel(self) -> Optional[Channel]:
        """Deleted message's channel.

        Returns
        -------
        Optional[:class:`Channel`]
        """
        return self.state.channels.get(self.__data.get("channel"))

    @property
    def deleted_at(self) -> datetime:
        """When deleted.

        Returns
        -------
        :class:`datetime`
        """
        return datetime.fromtimestamp(float(self.__data.get("ts", 0)))

    @property
    def hidden(self):
        """Is ephemeral.

        Returns
        -------
        :class:`bool`
        """
        return self.__data.get("hidden", False)
