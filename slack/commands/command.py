import functools
import logging
import traceback
from typing import Optional, Callable, Any

from .context import Context

__all__ = (
    "Command",
)

_logger = logging.getLogger(__name__)


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


class Command:
    """It's a class that represents a command

    .. versionadded:: 1.2.0

    Attributes
    ----------
    name: :class:`str`
        Comman name.
    """

    def __init__(self, func: Callable[..., Any], name: Optional[str] = None, *args, **kwargs):
        self.__func = func
        self.name = name or func.__name__
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other) -> bool:
        if isinstance(other, Command):
            return self.__func == other.__func
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

    # def __new__(cls, *args, **kwargs):
    #     return cls.__new__(cls)

    @property
    def callback(self) -> Callable:
        """It returns a function that is stored in the object

        Returns
        -------
        :class:`Callable`
             The function itself.

        """
        return self.__func

    async def invoke(self, ctx: Context):
        occur = _occur(self.__func)
        await occur(ctx, *ctx.args, **ctx.kwargs)
