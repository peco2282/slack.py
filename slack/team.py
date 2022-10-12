from __future__ import annotations

from typing import TYPE_CHECKING

from .types.team import (
    Icon as IconPayload,
    Team as TeamPayload
)

if TYPE_CHECKING:
    from .state import (
        ConnectionState
    )

__all__ = (
    "Icon",
    "Team"
)


class Icon:
    """This function is used to initialize the Icon class

    Parameters
    ----------
    team : :class:`~Team`
        The team that the icon is for.
    data : :class:`IconPayload`
        The data that was sent to the webhook.

    """
    def __init__(self, state: ConnectionState, team: "Team", data: IconPayload):
        self.data = data
        self.team = team


class Team:
    """This function takes in a TeamPayload object and sets the data attribute of the Team object to the TeamPayload object

    Attributes
    ----------
    state : :class:`~ConnectionState`
        The connection state.

    id : :class:`str`
        Team ID.

    url: :class:`bool`
        team link.

    icon: :class:`Icon`
        Team icon data.

    name: :class:`str`
        Team name.

    """
    def __init__(self, state: ConnectionState, data: TeamPayload):
        self.state = state
        self.id = data.get("id")
        self.name = data.get("name")
        self.url = data.get("url")
        self.domain = data.get("domain")
        self.email_domain = data.get("email_domain")
        self.icon = Icon(state, self, data.get("icon"))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
