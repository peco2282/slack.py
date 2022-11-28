import asyncio
import logging
import re
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

    def wait_for(
            self,
            event: str,
            check: Callable,
            timeout: Optional[float] = None,
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

        In case the event returns multiple arguments, a :class:`tuple` containing those
        arguments is returned instead. Please check the
        :ref:`documentation <discord-api-events>` for a list of events and their
        parameters.

        This function returns the **first event that meets the requirements**.

        Parameters
        ----------
        event: :class:`str`
            The event name, similar to the :ref:`event reference <discord-api-events>`,
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
            :ref:`event reference <discord-api-events>`.

        Raises
        ------
        asyncio.TimeoutError
            Raised if a timeout is provided and reached.

        Examples
        --------

        Waiting for a user reply: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$greet'):
                    channel = message.channel
                    await channel.send('Say hello!')

                    def check(m):
                        return m.content == 'hello' and m.channel == channel

                    msg = await client.wait_for('message', check=check)
                    await channel.send(f'Hello {msg.author}!')

        Waiting for a thumbs up reaction from the message author: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$thumb'):
                    channel = message.channel
                    await channel.send('Send me that \N{THUMBS UP SIGN} reaction, mate')

                    def check(reaction, user):
                        return user == message.author

                    try:
                        reaction, user = await client.wait_for('channel_create', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('\N{THUMBS DOWN SIGN}')
                    else:
                        await channel.send('\N{THUMBS UP SIGN}')
        """
        if not (event or isinstance(event, str)):
            raise TypeError("event param must be str.")

        future = self.loop.create_future()
        event = re.sub(r"^on_", event, "").lower()
        if not check:
            # noinspection PyUnusedLocal
            def _check(*args):
                return True
            check = _check
        listeners = self._listeners.get(event, [])
        listeners.append((future, check, timeout))
        self._listeners[event] = listeners

        return asyncio.wait_for(future, timeout)

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
