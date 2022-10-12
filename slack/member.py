from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .types.member import (
    Member as MemberPayload,
    Profile as ProfilePayload
)

if TYPE_CHECKING:
    from .state import ConnectionState

__all__ = (
    "Profile",
    "Member"
)


class Profile:
    """This function takes in a user and a data object and sets the user and data attributes of the Profile class to the
    user and data objects passed in

    Attributes
    ----------
    user : :class:`User`
        The user object that is being updated.
    phone: :class:`str`
        The phone number.

    status_text :class:`str`
        text of status.
    """
    def __init__(self, state: ConnectionState, user: "Member", data: ProfilePayload):
        self.user = user
        self.phone = data.get("phone")
        self.status_text = data.get("status_text")


# It creates a class called User.
class Member:
    """This function takes in a UserPayload object and assigns it to the data attribute of the User class

    Attributes
    ----------
    state : :class:`ConnectionState`
        The connection state.

    id : :class:`str`
        Your user ID.

    team : :class:`Team`
        Your team object.
    
    deleted: :class:`bool`
        Account was deleted.

    color: :class:`str`
        Account icon color.

    name: :class:`str`
        Account name.

    """
    def __init__(self, state: ConnectionState, data: MemberPayload):
        self.state = state
        self.id = data.get("id")
        self.team = state.teams[data.get("team_id")]
        self.deleted = data.get("deleted", False)
        self.color = data.get("color")
        self.real_name = data.get("real_name")
        self.tz = data.get("tz")
        self.tz_label = data.get("tz_label")
        self.tz_offset = data.get("tz_offset")
        self.profile = Profile(state, self, data.get("profile"))
        self.name = data.get("name")
        self.is_admin = data.get("is_admin", False)
        self.is_owner = data.get("is_owner")
        self.bot = data.get("is_bot")
        self.is_app_user = data.get("is_app_user")
        self.updated_at = datetime.fromtimestamp(data.get("updated"))
        self.is_email_confirmed = data.get("is_email_confirmed")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    @property
    def mention(self):
        return f"<@{self.id}>"
