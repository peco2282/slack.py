import asyncio
import functools
import traceback
from typing import Optional, Callable, Generic, TypeVar, ParamSpec

import slack
from .context import Context
from ..message import Message

__all__ = (
    "Client",
    "Command",
)

T = TypeVar("T")
P = ParamSpec("P")


def _occur(coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)

        except Exception as exc:
            traceback.TracebackException.from_exception(exc)
            raise exc

        return ret

    return wrapped


def inject(coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        ret = await coro(*args, **kwargs)
        return ret

    return wrapped


class Command(Generic[P, T]):
    """
    Attributes
    ----------
    func: :class:`Callable`

    """
    def __init__(self, func: Callable, name: Optional[str] = None, *args, **kwargs):
        self.func = func
        self.name = name or func.__name__
        self.args = args
        self.kwargs = kwargs

    # def __new__(cls, *args, **kwargs):
    #     return cls.__new__(cls)

    @property
    def callback(self):
        return self.func

    async def invoke(self, ctx: Context):
        occur = _occur(self.func)
        await occur(ctx, *ctx.args, **ctx.kwargs)


def command(name: Optional[str], **kwargs):
    def decorator(func: Callable):
        return Command(func=func, name=name, **kwargs)

    return decorator


class Client(slack.Client):
    """
    This is :class:`~slack.Client`'s subclass.

    Attributes
    ----------
    prefix: :class:`str`

    """

    def __init__(
            self,
            user_token: str,
            bot_token: str,
            token: str,

            prefix: Optional[str] = None,

            loop: Optional[asyncio.AbstractEventLoop] = None,
            **optional
    ):
        super().__init__(user_token, bot_token, token, loop, **optional)
        self.commands = {}
        self.prefix = str(prefix)

    def command(self, name: str = None, **kwargs):
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

            except AttributeError:
                pass

            except Exception as exc:
                traceback.TracebackException.from_exception(exc)
                self.dispatch("command_error", ctx, exc)

    async def process_commands(self, message: Message):
        content = message.content
        ctx = Context(client=self, message=message, prefix=self.prefix)
        ctx.name = content.split()[0].replace(self.prefix, "")
        ctx.command = self.commands.get(content.split()[0].replace(self.prefix, ""))
        ctx.args = content.split()[1:]
        await self.invoke_command(ctx)

    async def on_message(self, message):
        await self.process_commands(message)
