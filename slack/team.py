from __future__ import annotations

from typing import TYPE_CHECKING

from .route import Route
from .types.team import (
    Icon as IconPayload,
    Team as TeamPayload
)

if TYPE_CHECKING:
    from .state import ConnectionState
    from .channel import Channel
__all__ = (
    "Icon",
    "Team"
)


class Icon:
    """This function is used to initialize the Icon class

    Attributes
    ----------
    team : :class:`~Team`
        The team that the icon is for.

    image_default: :class:`bool`

    image_34: :class:`str`
        image url.

    image_44: :class:`str`

    image_68: :class:`str`

    image_88: :class:`str`

    image_102: :class:`str`

    image_230: :class:`str`

    image_132: :class:`str`

    """

    def __init__(self, state: ConnectionState, team: "Team", data: IconPayload):
        self.state = state
        self.team: Team = team
        self.image_default: bool = data.get("image_default", False)
        self.image_34: str | None = data.get("image_34")
        self.image_44: str | None = data.get("image_44")
        self.image_68: str | None = data.get("image_68")
        self.image_88: str | None = data.get("image_88")
        self.image_102: str | None = data.get("image_102")
        self.image_230: str | None = data.get("image_230")
        self.image_132: str | None = data.get("image_132")


class Team:
    """This function takes in a TeamPayload object and sets the data attribute of the Team object
    to the TeamPayload object

    Attributes
    ----------
    id : :class:`str`
        Team ID.

    url: :class:`bool`
        team link.

    icon: :class:`~Icon`
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
        self.icon: Icon = Icon(state, self, data.get("icon", {}))

    def __eq__(self, other) -> bool:
        if isinstance(other, Team):
            return self.id == other.id

        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    async def create_channel(self, name: str, join: bool = True) -> Channel:
        """
        Create new channel.

        Parameters
        ----------
        name: :class:`str`
            new channel name.

        join: :class:`bool`
            is bot join.

        Returns
        -------
        :class:`Channel`
            Return created channel.
        """
        channel = await self.state.http.create_channel(
            Route("POST", "conversations.create", self.state.http.bot_token),
            {"name": name}
        )
        if join:
            self.state.http.manage_channel(
                Route("POST", "conversations.join", self.state.http.bot_token),
                {"id": channel["channel"]["id"]}
            )

        return Channel(self.state, channel["channel"])
