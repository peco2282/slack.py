from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from slack import Message, commands, Channel, Team

if TYPE_CHECKING:
    from .command import Command


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
        # super().__init__(message.state)
        self.args = args
        self.kwargs = kwargs
        self.command: Optional[Command] = command
        self.name = ""
        self.client = client
        self.message = message
        self.prefix = prefix
        self.state = message.state

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
