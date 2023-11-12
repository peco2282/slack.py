from __future__ import annotations

import abc
import asyncio
import logging
import signal
import warnings
from typing import (
    Callable,
    TypeVar,
    Coroutine,
    Any,
    TYPE_CHECKING,
    final,
    overload
)

from . import utils
from .errors import TokenTypeException, InvalidArgumentException
from .httpclient import HTTPClient
from .state import ConnectionState
from .ws import SlackWebSocket

if TYPE_CHECKING:
    from .team import Team
    from .channel import Channel
    from .member import Member

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
T = TypeVar("T")


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


@final
class LoggerOption:
    __OPTIONS: dict[str, bool] = {}
    VALID_KEY = [
        "ready",
        "message",
        "message_update",
        "message_delete",
        "mention",
        "block_action",
        "channel_join",
        "reaction_added",
        "reaction_removed",
        "channel_create",
        "channel_delete",
        "channel_rename",
        "channel_unarchive",
        "member_join"
    ]

    @overload
    def __init__(self, **options: bool):
        ...

    def __init__(self, options: dict[str, bool]):
        self.__setoptions(options)

    def __setoptions(self, options: dict[str, bool]):
        for k in options.keys():
            if k not in LoggerOption.VALID_KEY:
                warnings.warn(k + " key is not available.", RuntimeWarning)
        self.__OPTIONS = options

    def set(self, key: str, state: bool):
        self.__OPTIONS[key] = state

    @property
    def keys(self) -> list[str]:
        return list(self.__OPTIONS.keys())

    def value(self, event: str):
        if event not in self.keys:
            return False

        return self.__OPTIONS[event]

    @classmethod
    def all(cls) -> LoggerOption:
        self = cls.__new__(cls)
        for k, _ in self.__OPTIONS.items():
            self.__OPTIONS[k] = True
        return self

    @classmethod
    def none(cls) -> LoggerOption:
        self = cls.__new__(cls)
        for k, _ in self.__OPTIONS.items():
            self.__OPTIONS[k] = False

        return self


class __Manager:
    _hash: int = -1
    _objects: dict[str, T] = {}

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return isinstance(other, (_TeamManager, _ChannelManager)) and other._hash != -1 and self._hash == other._hash

    __dict__ = _objects

    @abc.abstractmethod
    def __init__(self, _objects: dict[str, T]):
        self._objects = _objects
        self._hash = hash(_objects)
        raise NotImplementedError()

    @abc.abstractmethod
    def fetch(self, _id: str | int) -> T | None:
        raise NotImplementedError()

    get = fetch


class _TeamManager(__Manager):
    def __init__(self, _objects: dict[str, Team]):
        self.teams = _objects

    def fetch(self, _id: str | int) -> Team | None:
        return self.teams.get(str(_id))


class _ChannelManager(__Manager):

    def __init__(self, _objects: dict[str, Channel]):
        self.channels = _objects

    def fetch(self, _id: str | int) -> Channel | None:
        return self.channels.get(str(_id))


class Client:
    r"""Create `Client` object from params.
    Represents a client connection that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.

    A number of options can be passed to the :class:`Client`.

    Parameters
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

    debug: :class:`bool`
        Print announce in client object.

        .. versionadded:: 1.4.5
    """

    def __init__(
            self,
            user_token: str,
            bot_token: str,

            token: str | None = None,
            logger: logging.Logger | None = None,
            log_level: int = logging.INFO,
            log_format: logging.Formatter | None = None,

            loop: asyncio.AbstractEventLoop | None = None,

            logger_option: LoggerOption = LoggerOption.all(),
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

        self._ws: SlackWebSocket | None = None
        self._user_token: str = user_token
        self._bot_token: str = bot_token
        self._token: str | None = token
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self._closed: bool = False
        self._ready: asyncio.Event = asyncio.Event()
        self._handlers: dict[str, Callable[[], None]] = {
            "ready": self._handle_ready
        }
        self._logger = logger or logging.getLogger(__name__)
        self._debug = options.get("debug", True)
        utils.setup_logging(self._logger, log_level, log_format)

        self.http: HTTPClient = HTTPClient(
            self.loop,
            user_token=user_token,
            bot_token=bot_token,
            token=token,
            logger=logger
        )

        self.connection: ConnectionState = self._get_state(**options)
        # self._teams: list[dict[str, Any]]
        self._teams: dict[str, Team] = {}
        self._channels: dict[str, Channel] = {}
        self._members: dict[str, Member] = {}
        self._team_manager = _TeamManager({})
        self._channel_manager = _ChannelManager({})
        self._logger_option = logger_option if isinstance(logger_option, LoggerOption) else LoggerOption.all()
        if self._debug:
            self._logger.info("setup finished")

    def _get_state(self, **options) -> ConnectionState:
        return ConnectionState(
            dispatch=self.dispatch,
            http=self.http,
            loop=self.loop,
            handlers=self._handlers,
            logger=self._logger,
            client=self,
            **options
        )

    @property
    def team_manager(self) -> _TeamManager:
        """
        Teams manager.
            versionadded:: 1.4.5

        Returns
        -------
        _TeamManager
        """
        return self._team_manager

    @property
    def channel_manager(self) -> _ChannelManager:
        """
        Channels manager.
            versionadded:: 1.4.5

        Returns
        -------
        _ChannelManager
        """
        return self._channel_manager

    @property
    def teams(self) -> list[Team]:
        """
        List of teams.

        Returns
        -------
        list[:class:`Team`]

        """
        return list(self._teams.values())

    @property
    def channels(self) -> list[Channel]:
        """
        List of channels.

        Returns
        -------
        list[:class:`Channel`]
        """
        return list(self._channels.values())

    @property
    def members(self) -> list[Member]:
        """
        List of members.

        Returns
        -------
        list[:class:`Member`]

        """
        return list(self._members.values())

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @logger.setter
    def logger(self, _logger):
        raise ValueError("Logger value is not allow otherwise constructor.")

    def _handle_ready(self) -> None:
        return self._ready.set()

    def __log(self, event: str, method: str) -> None:
        if self._logger_option.value(event):
            self._logger.info("dispatch event %s", method)

    def dispatch(self, event: str, *args, **kwargs) -> None:
        method = f"on_{event}"
        try:
            coro: Coro = getattr(self, method)
            self.__log(event, method)

        except AttributeError:
            pass

        except Exception as e:
            self._logger.error("%s occured", type(e), exc_info=e)

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

        except NotImplementedError:
            pass

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
        self._logger.info("login successful with wss: %s", data.get("url"))
        self._teams, self._channels, self._members = await self.connection.initialize()
        self._team_manager = _TeamManager(self._teams)
        self._channel_manager = _ChannelManager(self._channels)
        await self.connect(data.get("url"))

    async def close(self) -> None:
        """Close connection.
        """
        self._closed = True
        self._logger.info("connection closed.")

    async def connect(self, ws_url: str) -> None:
        """
        connect to slack-API

        Parameters
        ----------
        ws_url : :class:`str`
        """
        while True:
            try:
                coro = SlackWebSocket.from_client(client=self, ws_url=ws_url, logger=self._logger)
                self._ws: SlackWebSocket = await asyncio.wait_for(coro, timeout=60.)
                if not self._ws:
                    break
                while True:
                    try:
                        await self._ws.poll_event()

                    except AttributeError:
                        break

            except Exception as e:
                self._logger.error("raise %s", e)
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
            self._logger.warning("%s", e)
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
        self._logger.error(f"{event_name} raise {exc.__class__.__name__} in {self.__class__.__name__}")
