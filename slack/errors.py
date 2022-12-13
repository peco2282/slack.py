from typing import Union


class SlackException(Exception):
    pass


class TokenTypeException(SlackException):
    pass


class InvalidArgumentException(SlackException):
    pass


class ForbiddenException(SlackException):
    pass


class RequestException(SlackException):
    pass


class ClientException(SlackException):
    pass


class RateLimitException(SlackException):
    pass


class BotException(ClientException):
    pass


SlackExceptions = Union[
    SlackException,
    TokenTypeException,
    InvalidArgumentException,
    ForbiddenException,
    RequestException,
    ClientException,
    RateLimitException,
    BotException
]
