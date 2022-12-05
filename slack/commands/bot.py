import asyncio
import logging
from typing import Optional, Dict, Callable

import slack
from slack.commands import Command, Context
from slack.errors import SlackException
from slack.message import Message

_logger = logging.getLogger(__name__)


def command(name: Optional[str], **kwargs):
    def decorator(func: Callable):
        return Command(func=func, name=name, **kwargs)

    return decorator


class Bot(slack.Client):
    """
    This is :class:`slack.Client`'s subclass.

    Attributes
    ----------
    prefix: :class:`str`
        Command-prefix.

    commands: Dict[str, :class:`Command`]
        command-name: Command-Obj.

    """

    def __init__(
            self,
            user_token: str,
            bot_token: str,
            token: str,

            prefix: str,

            loop: Optional[asyncio.AbstractEventLoop] = None,
            **optional
    ):
        super().__init__(user_token, bot_token, token, loop, **optional)
        self.commands: Dict[str, Command] = {}
        self.prefix = str(prefix)

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
        self.commands[name] = result

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
