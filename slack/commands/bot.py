from __future__ import annotations

import asyncio
import logging
from typing import (
    Callable,
    Optional, TypeVar,
)

import slack
from .command import Command
from .context import Context
from ..errors import SlackException
from ..message import Message

_logger = logging.getLogger(__name__)

# Coro = TypeVar("Coro", bound=Callable[..., Coroutine[..., ..., Any]])
# noinspection PyBroadException
try:
    Listener = TypeVar("Listener", bound=list[
        tuple[asyncio.Future, Callable[..., bool], Optional[float]]
    ])

except Exception:
    # noinspection PyTypeHints
    Listener = TypeVar("Listener")


def command(name: str | None, **kwargs):
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
            token: str | None,

            prefix: str,

            logger: logging.Logger | None = None,

            loop: asyncio.AbstractEventLoop | None = None,
            **optional
    ):
        super().__init__(
            user_token=user_token,
            bot_token=bot_token,
            token=token,
            logger=logger,
            loop=loop,
            **optional
        )
        self.__commands: dict[str, Command] = {}
        self.prefix = str(prefix)
        self._logger = logger
        self._listeners: dict[str, Listener] = {}

    @property
    def commands(self) -> dict[str, Command]:
        """Return all commands

        .. versionadded:: 1.4.0

        Returns
        -------
        Dict[`:class:`str`, :class:`Command`]
        """
        return self.__commands

    def get_command(self, name: str, /) -> Command | None:
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

    def command(self, name: str | None = None, **kwargs):
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

        else:
            self._logger.warning("%s", result.__class__.__name__, exc_info=TypeError())

    def wait_for(
            self,
            event: str,
            check: Callable[..., bool] | None = None,
            timeout: float | None = None,
    ):
        """|coro|

        Waits for a WebSocket event to be dispatched.

        This could be used to wait for a user to reply to a message,
        or to react to a message, or to edit a message in a self-contained
        way.

        The ``timeout`` parameter is passed onto :func:`asyncio.wait_for`. By default,
        it does not time out. Note that this does propagate the
        :exc:`asyncio.TimeoutError` for you in case of timeout and is provided for
        ease of use.

        Parameters
        ----------
        event: :class:`str`
            The event name, similar to the :ref:`event reference <api-events>`,
            but without the ``on_`` prefix, to wait for.
        check: Optional[Callable[..., :class:`bool`]]
            A predicate to check what to wait for. The arguments must meet the
            parameters of the event being waited for.
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out and raising
            :exc:`asyncio.TimeoutError`.

        Returns
        -------
        Any
            Returns no arguments, a single argument, or a :class:`tuple` of multiple
            arguments that mirrors the parameters passed in the
            :ref:`event reference <api-events>`.

        Raises
        ------
        asyncio.TimeoutError
            Raised if a timeout is provided and reached.

        Examples
        --------

        Waiting for a user reply: ::

            @bot.event
            async def on_message(message):
                if message.content.startswith('$greet'):
                    channel = message.channel
                    await channel.send('Say hello!')

                    def check(m):
                        return m.content == 'hello' and m.channel == channel

                    msg = await bot.wait_for('message', check=check)
                    await channel.send(f'Hello {msg.author}!')

        Waiting for a thumbs up reaction from the message author: ::

            @bot.event
            async def on_message(message):
                if message.content.startswith('$thumb'):
                    channel = message.channel
                    await channel.send('Send me that \N{THUMBS UP SIGN} reaction, mate')

                    def check(reaction, user):
                        return user == message.author

                    try:
                        reaction, user = await bot.wait_for('channel_create', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('\N{THUMBS DOWN SIGN}')
                    else:
                        await channel.send('\N{THUMBS UP SIGN}')
        """
        if not (event or isinstance(event, str)):
            raise TypeError("vent param must be str.")

        future = self.loop.create_future()
        event = event.lower()
        if check is None:
            # noinspection PyUnusedLocal
            def _check(*args):
                return True

            check = _check
        listeners: Listener = self._listeners.get(event, [])
        listeners.append((future, check, timeout))
        self._listeners[event] = listeners

        return asyncio.wait_for(future, timeout)

    def dispatch(self, event: str, *args, **kwargs) -> None:
        super().dispatch(event, *args, **kwargs)

        listeners = self._listeners.get(f"on_{event}")
        if listeners:
            removed = []
            future: asyncio.Future
            condition: Callable[..., bool]
            timeout: float | None
            for i, (future, condition, timeout) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)

                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)

                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                    removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(f"on_{event}")

            else:
                for index in reversed(removed):
                    del listeners[index]

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
        # noinspection PyShadowingNames
        command = self.commands.get(content.split()[0].replace(self.prefix, ""))
        if command:
            ctx = Context(
                client=self,
                message=message,
                prefix=self.prefix,
                command=self.commands[(
                    content.split()[0].replace(self.prefix, "")
                )]
            )
            ctx.name = content.split()[0].replace(self.prefix, "")
            ctx.args = tuple(content.split()[1:])
            await self.invoke_command(ctx)

    # async def on_message(self, message):
    #     await self.process_commands(message)
