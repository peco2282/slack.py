import asyncio
import logging
from typing import Optional, Dict, Callable

import slack
from .command import Command
from .context import Context
from ..errors import SlackException
from ..message import Message

_logger = logging.getLogger(__name__)


def command(name: Optional[str], **kwargs):
    def decorator(func: Callable):
        return Command(func=func, name=name, **kwargs)

    return decorator


class Bot(slack.Client):
    """
    This is :class:`slack.Client`'s subclass.

    .. versionadded:: 1.2.0

    Attributes
    ----------
    user_token: :class:`str`
        The your-self token. It must be start 'xoxp-...'

    bot_token: :class:`str`
        The bot token. It must be start 'xoxb-...'
    token: Optional[:class:`str`]
        App-level token. It is startwith 'xapp-...'

        .. versionchanged:: 1.4.0
            To optional.

    logger: :class:`Logger.Logger`
        Logger object.

        .. versionadded:: 1.4.0

    prefix: :class:`str`
        Command-prefix.

    """

    def __init__(
            self,
            user_token: str,
            bot_token: str,
            token: str,

            prefix: str,

            logger: logging.Logger = None,

            loop: Optional[asyncio.AbstractEventLoop] = None,
            **optional
    ):
        super().__init__(user_token, bot_token, token, loop, **optional)
        self.__commands: Dict[str, Command] = {}
        self.prefix = str(prefix)
        self._logger = logger or super().logger

    @property
    def commands(self) -> Dict[str, Command]:
        """Return all commands

        .. versionadded:: 1.4.0

        Returns
        -------
        Dict[`:class:`str`, :class:`Command`]
        """
        return self.__commands

    def get_command(self, name: str, /) -> Optional[Command]:
        """Get registered command from name

        .. versionadded:: 1.4.0

        Parameters
        ----------
        name: :class:`str`

        Returns
        -------
        Optional[:class:`Command`]
        """
        return self.__commands.get(name)

    def command(self, name: str = None, **kwargs):
        """
        Register command of your client-object.

        Parameters
        ----------
        name: :class:`str`
            command name.
            If you don't set, use function name.

        """

        def decorator(func):
            result = command(name, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def add_command(self, result: Command):
        name = result.name
        if isinstance(result, Command):
            self.__commands[name] = result

    async def invoke_command(self, ctx: Context):
        if ctx.command:
            # self.dispatch("command", ctx)

            try:
                await ctx.command.invoke(ctx)
                self.dispatch("command", ctx)
                self.dispatch("invoke", ctx)

            except AttributeError:
                pass

            except SlackException as exc:
                self.dispatch("command_error", ctx, exc)

            except Exception as exc:
                _logger.error("%s occured", type(exc), exc_info=exc)

    async def process_commands(self, message: Message):
        content = message.content
        ctx = Context(client=self, message=message, prefix=self.prefix)
        ctx.name = content.split()[0].replace(self.prefix, "")
        ctx.command = self.commands.get(content.split()[0].replace(self.prefix, ""))
        ctx.args = content.split()[1:]
        await self.invoke_command(ctx)

    async def on_message(self, message):
        await self.process_commands(message)
