from datetime import datetime
from typing import Dict

from .errors import *

errors: Dict[str, SlackExceptions] = {
    "invalid_auth": TokenTypeException("Some aspect of authentication cannot be validated."),
    "missing_args": ClientException("An app-level token wasn't provided."),
    "internal_error": SlackException("The server could not complete your operation(s) without encountering an error"),
    "forbidden_team": ForbiddenException("The authenticated team cannot use."),
    "not_authed": TokenTypeException("No authentication token provided."),
    "account_inactive": TokenTypeException("Authentication token is for a deleted user or workspace when using a bot "
                                           "token."),
    "token_revoked": ClientException("Authentication token is for a deleted user or workspace or the app has been "
                                     "removed when using a user token.")
}


def ts2time(time: str) -> datetime:
    return datetime.fromtimestamp(float(time))


def parse_exception(event_name: str):
    exc = errors.get(event_name)
    if exc is None:
        exc = SlackException()

    raise exc
