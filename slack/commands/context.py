from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, overload

from typing_extensions import ParamSpec

from slack import commands
from ..channel import Channel
from ..errors import InvalidArgumentException
from ..message import Message, DeletedMessage
from ..route import Route
from ..team import Team
from ..view import ViewFrame

if TYPE_CHECKING:
    from .bot import Bot
    from .command import Command

    P = ParamSpec("P")

else:
    P = TypeVar("P")

BotT = TypeVar("BotT", bound=Bot)


class Context(Message):
    """A context is a message that is sent to a handler

    Attributes
    ----------
    client: :class:`Bot`
    message: :class:`.Message`
        Message object of context.

    id: :class:`str`
        Context ID (equals message ID)

    channel_id: :class:`str`
        Context channel ID

    prefix: :class:`str`
        Message prefix.
    """

    def __init__(
            self,
            client: commands.Bot,
            message: Message,
            prefix: str,
            command: Optional[Command] = None,
            *args,
            **kwargs
    ):
        self.args = args
        self.kwargs = kwargs
        self.command: Optional[Command] = command
        self.name = ""
        self.client = client
        self.message = message
        self.prefix = prefix
        self.state = message.state
        self.id = message.id
        self.channel_id = self.channel.id

    def __eq__(self, other) -> bool:
        if isinstance(other, Context):
            return self.command.callback == other.command.callback
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id{self.id}>"

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
            "channel": self.channel_id,
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
        return DeletedMessage(self.state, message.get("message"))

    @overload
    async def send(
            self,
            text: str = ...,
    ) -> Context:
        ...

    @overload
    async def send(
            self,
            view: ViewFrame = ...
    ) -> Context:
        ...

    async def send(
            self,
            text: Optional[str] = None,
            view: Optional[ViewFrame] = None
    ) -> Context:
        """Send message.
        Parameters must required `text or view`.

        Parameters
        ----------
        text: Optional[:class:`str`]
        view: Optional[:class:`View`]

        Returns
        -------
        :class:`Context`
            Context object contains message.
        """
        if (text is not None and view is not None) or (text is None and view is None):
            raise InvalidArgumentException()
        if view is not None:
            message = await self.message.channel.send(
                view=view
            )

        elif text is not None:
            message = await self.message.channel.send(
                text=text
            )

        else:
            raise ValueError()

        return Context(
            client=self.client,
            message=message,
            prefix=self.prefix,
            command=self.command
        )
