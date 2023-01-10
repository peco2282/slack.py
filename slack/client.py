from __future__ import annotations

import asyncio
import logging
import signal
import traceback
from typing import (
    List,
    Dict,
    Callable,
    TypeVar,
    Coroutine,
    Any,
    Optional,
    TYPE_CHECKING
)

from .errors import TokenTypeException, InvalidArgumentException
from .httpclient import HTTPClient
from .state import ConnectionState
from .ws import SlackWebSocket

if TYPE_CHECKING:
    from .team import Team
    from .channel import Channel
    from .member import Member

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])

_logger = logging.getLogger(__name__)


def cancel_task(loop: asyncio.AbstractEventLoop):
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    for task in tasks:
        if task.cancelled():
            continue

        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during Client.run shutdown.",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def result_task(loop: asyncio.AbstractEventLoop):
    try:
        cancel_task(loop=loop)
        loop.run_until_complete(loop.shutdown_asyncgens())

    finally:
        loop.close()


class Client:
    r"""Create `Client` object from params.
    Represents a client connection that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.

    A number of options can be passed to the :class:`Client`.

    Attributes
    -----------
    user_token: :class:`str`
        The your-self token. It must be start 'xoxp-...'
    bot_token: :class:`str`
        The bot token. It must be start 'xoxb-...'
    token: Optional[:class:`str`]
        App-level token. It is startwith 'xapp-...'

        .. versionchanged:: 1.4.0
            To optional.

    logger: Optional[:class:`Logger.Logger`]
        Logger object.

        .. versionadded:: 1.4.0

    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        :func:`asyncio.get_event_loop()`.
    """

    def __init__(
            self,
            user_token: str,
            bot_token: str,

            token: Optional[str] = None,
            logger: Optional[logging.Logger] = None,

            loop: Optional[asyncio.AbstractEventLoop] = None,
            **options
    ):

        if not all([isinstance(t, str) for t in (user_token, bot_token)]):
            raise TypeError("All token must be `str`")

        if user_token is not None and not user_token.startswith("xoxp-"):
            raise TokenTypeException("User token must be start `xoxp-`")

        if bot_token is not None and not bot_token.startswith("xoxb-"):
            raise TokenTypeException("Application token must be start `xoxb-`")

        if (user_token is None) and (bot_token is None):
            raise InvalidArgumentException("`user_token` and `bot_token` are required.")

        if token is not None and not token.startswith("xapp-"):
            raise TokenTypeException("Token must be start `xapp-`")

        self.ws: Optional[SlackWebSocket] = None
        self.user_token: str = user_token
        self.bot_token: str = bot_token
        self.token: Optional[str] = token
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.http: HTTPClient = HTTPClient(self.loop, user_token=user_token, bot_token=bot_token, token=token)
        self._closed: bool = False
        self._ready: asyncio.Event = asyncio.Event()
        self._handlers: Dict[str, Callable] = {
            "ready": self._handle_ready
        }
        self.logger = logger or _logger
        self.connection: ConnectionState = self._get_state(**options)
        self._teams: List[Dict[str, Any]]
        self._teams: Dict[str, Team] = {}
        self._channels: Dict[str, Channel] = {}
        self._members: Dict[str, Member] = {}

    def _get_state(self, **options) -> ConnectionState:
        return ConnectionState(
            dispatch=self.dispatch,
            http=self.http,
            loop=self.loop,
            handlers=self._handlers,
            **options
        )

    @property
    def teams(self) -> List[Team]:
        """
        List of teams.

        Returns
        -------
        list[:class:`Team`]

        """
        return list(self._teams.values())

    @property
    def channels(self) -> List[Channel]:
        """
        List of channels.

        Returns
        -------
        list[:class:`Channel`]
        """
        return list(self._channels.values())

    @property
    def members(self) -> List[Member]:
        """
        List of members.

        Returns
        -------
        list[:class:`Member`]

        """
        return list(self._members.values())

    def _handle_ready(self) -> None:
        return self._ready.set()

    def dispatch(self, event: str, *args, **kwargs) -> None:
        method = f"on_{event}"
        try:
            coro: Coro = getattr(self, method)
            _logger.info("dispatch event %s", method)

        except AttributeError:
            pass

        except Exception as e:
            self.logger.error("%s occured", type(e), exc_info=e)

        else:
            self._schedule_event(coro, method, *args, **kwargs)

    def is_closed(self) -> bool:
        """It returns a boolean value.

        Returns
        -------
        :class:`bool`
            The return value is a boolean value.

        """
        return self._closed

    def event(self, coro: Coro) -> Coro:
        """`event` is a decorator that takes a coroutine function and sets
         it as an attribute of the class it's decorating.

        Parameters
        ----------
        coro : :class:`Coro`
            The coroutine function to be decorated.

        Returns
        -------
            The coro function itself.

        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event must be coroutine function.")

        setattr(self, coro.__name__, coro)
        _logger.info("%s event set", coro.__name__)
        return coro

    def run(self) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.
        If you want more control over the event loop then this
        function should not be used. Use :meth:`start` coroutine
        or :meth:`connect` + :meth:`login`.
        Roughly Equivalent to: ::

            try:
                loop.run_until_complete(start(*args, **kwargs))
            except KeyboardInterrupt:
                loop.run_until_complete(close())
                # cancel all tasks lingering
            finally:
                loop.close()

        .. warning::
            This function must be the last function to call due to the fact that it
            is blocking. That means that registration of events or anything being
            called after this function call will not execute until it returns.
        """

        loop: asyncio.AbstractEventLoop = self.loop
        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)

        except NotImplementedError as nie:
            _logger.error(traceback.TracebackException.from_exception(nie))

        async def runner() -> None:
            try:
                await self.start()

            finally:
                if not self.is_closed():
                    await self.close()

        # noinspection PyUnusedLocal
        def stop_loop(f) -> None:
            loop.stop()

        future: asyncio.Task = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            pass

        finally:
            future.remove_done_callback(stop_loop)
            result_task(loop)

        if not future.cancelled():
            try:
                return future.result()

            except KeyboardInterrupt:
                return None

    async def start(self) -> None:
        """
        start connection.
        """
        await self.login()

    async def login(self) -> None:
        """
        Login as bot with websocket.
        Get teams, channels and member data.
        """
        data = await self.http.login()
        self._teams, self._channels, self._members = await self.connection.initialize()
        await self.connect(data.get("url"))

    async def close(self) -> None:
        """Close connection.
        """
        self._closed = True

    async def connect(self, ws_url: str) -> None:
        """
        connect to slack-API

        Parameters
        ----------
        ws_url : :class:`str`
        """
        while True:
            try:
                coro = SlackWebSocket.from_client(client=self, ws_url=ws_url, logger=self.logger)
                self.ws: SlackWebSocket = await asyncio.wait_for(coro, timeout=60.)
                if not self.ws:
                    break
                while True:
                    await self.ws.poll_event()

            except Exception as e:
                _logger.error("raise %s", e)
                raise e

    def _schedule_event(
            self,
            coro: Callable[..., Coroutine[Any, Any, Any]],
            event_name: str,
            *args,
            **kwargs
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return asyncio.create_task(wrapped, name=f"with: {event_name}")

    async def _run_event(
            self,
            coro: Coro,
            event_name: str,
            *args,
            **kwargs
    ) -> None:
        try:
            await coro(*args, **kwargs)

        except asyncio.CancelledError as e:
            _logger.warning("%s", e)
            pass

        except Exception as exc:
            await self.on_error(event_name, exc, *args, **kwargs)
            raise exc

    # noinspection PyUnusedLocal
    async def on_error(self, event_name, exc: Exception, *args, **kwargs) -> None:
        """It prints the name of the event that raised the exception, the name of the exception, and the name of the
        class that the event is in.

        Parameters
        ----------
        event_name
            The name of the event that was raised.
        exc : Exception
            The exception that was raised.

        """
        _logger.error(f"{event_name} raise {exc.__class__.__name__} in {self.__class__.__name__}")
