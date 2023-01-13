from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic

from typing_extensions import ParamSpec

import slack.base
from slack import commands
from slack.channel import Channel
from slack.message import Message, DeletedMessage
from slack.route import Route
from slack.team import Team

if TYPE_CHECKING:
    from .command import Command
    from .bot import Bot
    from slack.member import Member

    P = ParamSpec("P")

else:
    P = TypeVar("P")

BotT = TypeVar("BotT", bound="Bot")


class Context(slack.base.Sendable, Generic[BotT]):
    """A context is a message that is sent to a handler

    Attributes
    ----------
    client: :class:`Bot`
    message: :class:`.Message`
        Message object of context.

    message_id: :class:`str`
        Context ID (equals message ID)

    id: :class:`str`
        Context channel ID

    prefix: :class:`str`
        Message prefix.
    """

    def __init__(
            self,
            client: commands.Bot,
            message: Message,
            prefix: str,
            command: Command,
            *args,
            **kwargs
    ):
        self.args = args
        self.kwargs = kwargs
        self.command: Command = command
        self.name = ""
        self.client = client
        self.message = message
        self.prefix = prefix
        self.state = message.state
        self.message_id = message.id
        self.id = self.channel.id  # channel_id
        self.http = client.http

    def __eq__(self, other) -> bool:
        if isinstance(other, Context):
            try:
                return self.command.callback == other.command.callback

            except AttributeError:
                return False
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id{self.id}>"

    @property
    def author(self) -> Member:
        return self.message.author

    @property
    def channel(self) -> Channel:
        """Returns context channel.

        Returns
        -------
        :class:`Channel`
            Context channel.
        """
        return self.message.channel

    @property
    def team(self) -> Team:
        """Return context team.

        Returns
        -------
        :class:`Team`
            Context team.
        """
        return self.message.team

    async def delete(self) -> DeletedMessage:
        """Delete context message.

        Returns
        -------
        :class:`DeletedMessage`
            Data of deleted message.

        """
        param = {
            "channel": self.id,
            "ts": self.id
        }
        message = await self.state.http.delete_message(
            Route(
                "DELETE",
                "chat.delete",
                self.state.http.bot_token
            ),
            param
        )
        return DeletedMessage(self.state, message.get("message", {}))
