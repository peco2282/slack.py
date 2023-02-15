from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .errors import SlackException, InvalidArgumentException
from .route import Route
from .utils import ts2time

if TYPE_CHECKING:
    from .team import Team
    from .state import ConnectionState
    from .member import Member
    from .channel import Channel

# noinspection PyProtectedMember
from .types.message import (
    _Edited,
    Message as MessagePayload,
    JoinMessage as JoinMessagePayload,
    PurposeMessage as PurposeMessagePayload,
    PreviousMessage as PreviousMessagePayload,
    DeletedMessage as DeletedMessagePayload,
    ArchivedMessage as ArchivedMessagePayload,
    ReactionComponent as ReactionComponentPayload
)

__all__ = (
    "ReactionComponent",
    "Message",
    "JoinMessage",
    "PurposeMessage",
    "DeletedMessage",
)


class ReactionComponent:
    """
    Information of reaction.

    Attributes
    ----------
    name: :class:str`
        Reaction name.

    members: List[:class:`Member`]
        A list of reacted members.
        Always contain the authenticated user, but might not always contain all users that have reacted.

    count: :class:`int`
        Represent the count of all users who made that reaction.
    """
    def __init__(self, state: ConnectionState, data: ReactionComponentPayload):
        self.name: str = data["name"]
        self.__users: list[str] = data["users"]
        self.members: list[Member] = [state.members[member] for member in self.__users]
        self.count: int = int(data["count"])


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

    """

    def __init__(self, state: ConnectionState, data: MessagePayload):
        self.state = state
        self.team_id = data.get("team")
        self.id = data.get("ts")
        self.user_id: str = data.get("user")
        self.channel_id: str = data.get("channel")
        self.content: str = data.get("text", "")
        # self.created_at: Optional[datetime] = ts2time(float(self.id)) if self.id else None
        self.blocks: list[dict[str, Any]] = data.get("blocks")
        self.scheduled_message_id: str | None = None
        self.__edited: _Edited | None = data.get("edited")
        # self.__edited_ts: str = self.__edited.get("ts") if self.__edited else self.id
        self.__edited_user: Member | None = self.state.members.get(
            self.__edited.get("user")) if self.__edited else None
        # self.edited_at = ts2time(float(self.__edited_ts))
        self.all_reactions: list[ReactionComponent | None] = [
            ReactionComponent(state, c) for c in data.get("reactions", [])
        ]

    def __eq__(self, other) -> bool:
        if isinstance(other, Message):
            return self.id == other.id

        return False

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} channel_id={self.channel_id}>"

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 1.4.3

        Returns
        -------
        :class:`datetime`
            Returns the date and time of transmission.
        """
        return ts2time(self.id)

    @property
    def edited_at(self) -> datetime:
        """

        .. versionadded:: 1.4.3

        Returns
        -------
        :class:`datetime`
            Returns when it was edited.
            If not edited, returns the sender.
        """
        if self.__edited is None:
            return self.created_at

        return ts2time(self.__edited.get("ts"))

    @property
    def edited_by(self) -> Member:
        """

        .. versionadded:: 1.4.3

        Returns
        -------
        :class:`Member`
            Returns who edited the file.
            If not edited, returns the sender.
        """
        if self.__edited_user is not None:
            return self.__edited_user

        return self.author

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
    def author(self) -> Member:
        """Message author.

        Returns
        -------
        :class:`Member`
            Message author.

        """
        return self.state.members[self.user_id]

    @property
    def team(self) -> Team:
        """Message team.

        Returns
        -------
        :class:`Team`
            Message team.

        """
        return self.state.teams[self.team_id]

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
        msg = rtn["message"]
        msg["ts"] = rtn["ts"]
        return Message(self.state, msg)

    async def delete(self) -> DeletedMessage:
        """It deletes a message.

        Returns
        -------
        :class:`DeletedMessage`
            A DeletedMessage object.

            .. versionchanged:: 1.4.0
                Return :class:`DeletedMessage`
        """
        param = {
            "channel": self.channel_id,
            "ts": self.id
        }
        try:
            rtn = await self.state.http.delete_message(
                Route(
                    "DELETE",
                    "chat.delete",
                    self.state.http.bot_token
                ),
                param
            )
        except SlackException:
            try:
                rtn = await self.state.http.delete_message(
                    Route(
                        "DELETE",
                        "chat.delete",
                        self.state.http.user_token
                    ),
                    param
                )
            except SlackException as exc:
                raise exc
        return DeletedMessage(self.state, rtn)

    async def reply(self, text: str):
        """
        Create thread to this message.

        .. versionadded:: 1.4.3

        Parameters
        ----------
        text: :class:`str`
            Text you want reply.

        Returns
        -------
        :class:`Message`
            Sended message.
        """
        param = {
            "channel": self.channel_id,
            "thread_ts": self.id,
            "text": str(text)
        }
        rtn = await self.state.http.send_message(
            Route("POST", "chat.postMessage", self.state.http.bot_token),
            query=param
        )
        return Message(self.state, rtn["message"])

    async def replies(self) -> list[Message]:
        """
        Get replied message from message id.

        .. versionadded:: 1.4.3

        Returns
        -------
        List[:class:`Message`]
            Returns original message and replied messages.
        """
        rtn = await self.state.http.send_message(
            Route("GET", "conversations.replies", self.state.http.bot_token),
            query={
                "channel": self.channel.id,
                "ts": self.id
            }
        )
        return [Message(self.state, message) for message in rtn.get("messages", {})]

    async def reaction_add(self, name: str, skin_tone_level: int | None = None) -> None:
        """
        Add a reaction to the specified message.

        ..versionadded:: 1.4.3

        Parameters
        ----------
        name: :class:`str`
            Reaction name. See `this URL <https://emojipedia.org/>`_ for supported reactions.

        skin_tone_level: :class:`int`

        """
        if skin_tone_level is not None and isinstance(skin_tone_level, int):
            if not 2 <= skin_tone_level <= 6:
                raise InvalidArgumentException("`skin_tone_level` must be between 2 and 6.")

            name = str(name) + f"::skin-tone-{skin_tone_level}"

        query = {
            "ts": self.id,
            "channel": self.channel_id,
            "name": str(name)
        }
        try:
            await self.state.http.post_anything(
                Route("POST", "reactions.add", self.state.http.bot_token),
                query=query
            )

        except SlackException:  # If the name of the reaction is incorrect.
            pass

    async def reactions(self) -> list[ReactionComponent]:
        """
        Returns a list of reactions given to the specified message.

        ..versionadded:: 1.4.3

        Returns
        -------
        List[:class:`ReactionComponent`]
        """
        query = {
            "timestamp": self.id,
            "channel": self.channel_id
        }
        rtn = await self.state.http.send_message(
            Route("GET", "reactions.get", self.state.http.bot_token),
            query=query
        )
        reactions = rtn["message"].get("reactions")
        reaction_list = []
        if reactions is not None:
            reaction_list = [
                ReactionComponent(self.state, r) for r in reactions
            ]
        return reaction_list

    async def reaction_remove(self, name: str):
        """

        Parameters
        ----------
        name: :class:`str`
            A reaction name you want to remove.

        Returns
        -------

        """
        query = {
            "name": str(name)
        }
        await self.state.http.post_anything(
            Route("POST", "reactions.remove", self.state.http.bot_token),
            query=query
        )


class JoinMessage(Message):
    """
    This function is a constructor for the JoinMessage class. It takes in a ConnectionState and a JoinMessagePayload as
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
        self.user = self.state.members.get(data.get("user", ""))
        self.team = self.state.teams.get(data.get("team", ""))
        self.ts = datetime.fromtimestamp(float(data["ts"]))


class DeletedMessage:
    """This function is used to delete a message from a channel
    """

    def __init__(self, state: ConnectionState, data: DeletedMessagePayload):
        self.__data = data
        self.state = state
        # self.previous_message: PreviousMessage = PreviousMessage(self.state, data.get("previous_message"))
        # self.hidden: bool = data.get("hidden", False)
        # self.deleted_text: str = self.previous_message.text

    @property
    def channel(self) -> Channel | None:
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
        self.user: Member = self.state.members.get(data.get("user", ""))
        self.channel: Channel = self.state.channels.get(data.get("channel", ""))
        # self.channel_type = data.get("channel_type")
