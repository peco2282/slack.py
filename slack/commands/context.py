from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, overload

from typing_extensions import ParamSpec

from .. import commands
from ..channel import Channel
from ..errors import InvalidArgumentException
from ..message import Message
from ..route import Route
from ..team import Team
from ..view import ViewFrame

if TYPE_CHECKING:
    from .command import Command

    P = ParamSpec("P")

else:
    P = TypeVar("P")

BotT = TypeVar("BotT", bound="Bot")


class Context(Message):
    """
    Attributes
    ----------
    message: :class:`.Message`
        Message object of context.

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

    @property
    def channel(self) -> Channel:
        """Returns context channel.

        Returns
        -------
        :class:`Channel`
        """
        return self.message.channel

    @property
    def team(self) -> Team:
        """Return context team.

        Returns
        -------
        :class:`Team`
        """
        return self.message.team

    async def delete(self):
        param = {
            "channel": self.channel_id,
            "ts": self.id
        }
        await self.state.http.delete_message(
            Route(
                "DELETE",
                "chat.delete",
                self.state.http.bot_token
            ),
            param
        )

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
        """

        Parameters
        ----------
        text: Optional[:class:`str`]
        view: Optional[:class:`View`]

        Returns
        -------
        :class:`Context`

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
