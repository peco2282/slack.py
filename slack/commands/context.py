from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar

from typing_extensions import ParamSpec

from slack import Message, commands, Channel, Team, Route

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

    async def send(self, text: str) -> Message:
        """|coroutine|

        It sends a message to a channel.

        Parameters
        ----------
        text : :class:`str`
            The text of the message to send.

        Returns
        -------
        :class:`~Message`
            A Message object.

        """
        param = {
            "channel": self.id,
            "text": text
        }
        message = await self.state.http.send_message(
            Route("POST", "chat.postMessage", token=self.state.http.bot_token),
            param
        )
        msg = Message(state=self.state, data=message["message"])
        msg.channel_id = self.id
        return msg
