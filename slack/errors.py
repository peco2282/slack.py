class SlackException(Exception):
    pass


class TokenTypeException(SlackException):
    pass


class RequestException(SlackException):
    pass


class ClientException(SlackException):
    pass


class RateLimitException(SlackException):
    pass


class BotException(ClientException):
    pass
