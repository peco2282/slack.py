from __future__ import annotations

import functools
import logging
import os
import sys
import warnings
from datetime import datetime
from operator import attrgetter
from typing import Any, TypeVar, Iterable, Generator, overload, Callable

from .errors import *

errors: dict[str, SlackExceptions] = {
    "invalid_auth": TokenTypeException("Some aspect of authentication cannot be validated."),
    "missing_args": ClientException("An app-level token wasn't provided."),
    "missing_scope": "",
    "internal_error": SlackException("The server could not complete your operation(s) without encountering an error"),
    "forbidden_team": ForbiddenException("The authenticated team cannot use."),
    "not_authed": TokenTypeException("No authentication token provided."),
    "account_inactive": TokenTypeException("Authentication token is for a deleted user or workspace when using a bot "
                                           "token."),
    "token_revoked": ClientException("Authentication token is for a deleted user or workspace or the app has been "
                                     "removed when using a user token."),
    "invalid_blocks": InvalidArgumentException("Blocks submitted with this message are not valid"),
    "invalid_blocks_format": InvalidArgumentException("The blocks is not a valid JSON object or doesn't match the "
                                                      "Block Kit syntax.")
}

# https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences#text-formatting
DEFAULT = 0
UNDERLINE = 4
NO_UNDERLINE = 24

FOREGROUND_BLACK = 30
FOREGROUND_RED = 31
FOREGROUND_GREEN = 32
FOREGROUND_YELLOW = 33
FOREGROUND_BLUE = 34
FOREGROUND_MAGENTA = 35
FOREGROUND_CYAN = 36
FOREGROUND_WHITE = 37

BACKGROUND_BLACK = 40
BACKGROUND_RED = 41
BACKGROUND_GREEN = 42
BACKGROUND_YELLOW = 43
BACKGROUND_BLUE = 44
BACKGROUND_MAGENTA = 45
BACKGROUND_CYAN = 46
BACKGROUND_WHITE = 47

BLIGHT_FOREGROUND_BLACK = 90
BLIGHT_FOREGROUND_RED = 91
BLIGHT_FOREGROUND_GREEN = 92
BLIGHT_FOREGROUND_YELLOW = 93
BLIGHT_FOREGROUND_BLUE = 94
BLIGHT_FOREGROUND_MAGENTA = 95
BLIGHT_FOREGROUND_CYAN = 96
BLIGHT_FOREGROUND_WHITE = 97

BLIGHT_BACKGROUND_BLACK = 100
BLIGHT_BACKGROUND_RED = 101
BLIGHT_BACKGROUND_GREEN = 102
BLIGHT_BACKGROUND_YELLOW = 103
BLIGHT_BACKGROUND_BLUE = 104
BLIGHT_BACKGROUND_MAGENTA = 105
BLIGHT_BACKGROUND_CYAN = 106
BLIGHT_BACKGROUND_WHITE = 107


def ts2time(time: str | int | float | None) -> datetime | None:
    if time is None:
        return None
    return datetime.fromtimestamp(float(time))


def parse_exception(event_name: str, **kwargs):
    if event_name == "missing_scope":
        needed = kwargs.get("needed", "").split(",")
        provided = kwargs.get("provided", "").split(",")
        raise ClientException("missing_scope: {}, provided: {}".format(", ".join(needed), ", ".join(provided)))
    exc = errors.get(event_name)
    if exc is None:
        exc = SlackException(event_name)

    raise exc


T = TypeVar("T")


@overload
def get(iterator: Iterable[T]) -> Generator[T]:
    ...


def get(iterator: Iterable[T], /, **kwargs) -> Generator[T]:
    """

    Parameters
    ----------
    iterator
    kwargs

    Returns
    -------
    Generator object contain matched keyword(s).
    """
    if len(kwargs) == 0:
        for i in iterator:
            yield i

    else:
        flag = True
        converted: list[tuple[attrgetter, Any]] = [(attrgetter(k.replace("__", ".")), v) for k, v in kwargs.items()]
        for i, elem in enumerate(iterator):
            if all(agetter(elem) == v for agetter, v in converted):
                flag = False
                yield elem

        if flag:
            yield None


def deprecated(newfunc: str):
    def wrapper(func: Callable[[Any], Any]):
        # noinspection PyUnusedLocal
        def inner(*args, **kwargs):
            warnings.warn(f"method \"{func.__name__}\" will be replace \"{newfunc}\"", stacklevel=3)

        return inner

    return wrapper


def notnone(func: Callable[[Any], Any]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        null = []
        for i, arg in enumerate(args, 1):
            if arg is None:
                null.append(f"{i}")
        string = ", ".join(null) + " parameter(s) is None" if len(null) != 0 else ""
        null = []
        for k, v in kwargs.items():
            if v is None:
                null.append(f"`{k}`")
        string += " " + ", ".join(null) + " keyword is None" if len(null) != 0 else ""
        if len(string) != 0:
            warnings.warn(string, stacklevel=3)

    return wrapper


class _Formatter(logging.Formatter):
    COLORS: tuple[tuple[int, int]] = (
        (logging.NOTSET, FOREGROUND_WHITE),
        (logging.DEBUG, FOREGROUND_WHITE),
        (logging.INFO, BACKGROUND_GREEN),
        (logging.WARNING, FOREGROUND_YELLOW),
        (logging.ERROR, FOREGROUND_RED),
        (logging.CRITICAL, FOREGROUND_RED)
    )
    FORMAT: dict[int, logging.Formatter] = {
        lv: logging.Formatter(
            f"\x1b[{FOREGROUND_CYAN}m%(asctime)s\x1b[0m \x1b[{cl}m\x1b[{BLIGHT_BACKGROUND_BLACK}m"
            f"%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m \x1b[{FOREGROUND_GREEN}m%(message)s",
            "%Y-%m-%d %H:%M:%S"
        ) for lv, cl in COLORS
    }

    def format(self, record: logging.LogRecord) -> str:
        _format = self.FORMAT.get(record.levelno, logging.DEBUG)
        if record.exc_info:
            text = _format.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = _format.format(record)
        record.exc_text = None
        return output


INVALID_HANDLE_VALUE = -1
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
ENABLE_LVB_GRID_WORLDWIDE = 0x0010


def enable():
    if sys.platform != "win32":
        return

    from ctypes import windll, wintypes, byref
    out = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    if out == INVALID_HANDLE_VALUE:
        return False
    dw_mode = wintypes.DWORD()
    if windll.kernel32.GetConsoleMode(out, byref(dw_mode)) == 0:
        return False
    dw_mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
    # dwMode.value |= ENABLE_LVB_GRID_WORLDWIDE
    if windll.kernel32.SetConsoleMode(out, dw_mode) == 0:
        return False
    return True


def stream_supports_colour(stream: Any) -> bool:
    # Pycharm and Vscode support colour in their inbuilt editors
    if 'PYCHARM_HOSTED' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode':
        return True

    is_a_tty = hasattr(stream, 'isatty') and stream.isatty()
    # if sys.platform != 'win32':
    #     # Docker does not consistently have a tty attached to it
    #     return is_a_tty or is_docker()

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    return is_a_tty and ('ANSICON' in os.environ or 'WT_SESSION' in os.environ)


def setup_logging(logger: logging.Logger, level: int = logging.INFO, log_format: logging.Formatter | None = None):
    enable()
    handler = logging.StreamHandler()
    if log_format is None or not isinstance(log_format, logging.Formatter):
        if stream_supports_colour(handler.stream):
            log_format = _Formatter()

        else:
            dt_fmt = '%Y-%m-%d %H:%M:%S'
            log_format = logging.Formatter(
                '[{asctime}] [{levelname:<8}] {name}: {message}',
                dt_fmt,
                style='{'
            )
    handler.setFormatter(log_format)

    logger.setLevel(level)
    logger.addHandler(handler)
