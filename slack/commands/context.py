from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from slack import Message, commands

if TYPE_CHECKING:
    from .command import Command


class Context(Message):
    """
    Attributes
    ----------
    command: :class:`Optional[.Command]`
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
        # super().__init__(message.state)
        self.args = args
        self.kwargs = kwargs
        self.command: Optional[Command] = command
        self.name = ""
        self.client = client
        self.message = message
        self.prefix = prefix
        self.state = message.state

    async def invoke(self, command, *args, **kwargs):
        return await command(self, *args, **kwargs)
