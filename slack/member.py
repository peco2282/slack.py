from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .team import Team
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
    user : :class:`Member`
        The user object that is being updated.

    phone: :class:`str`
        The phone number.

    status_text: :class:`str`
        text of status.

    skype: :class:`str`
        skype user name.

    team: Optional[:class:`Team`]
        team data.

    """

    def __init__(self, state: ConnectionState, user: "Member", data: ProfilePayload):
        self.state = state
        self.user = user
        self.phone = data.get("phone")
        self.skype = data.get("skype")
        self.real_name = data.get("real_name")
        self.real_name_normalized = data.get("real_name_normalized")
        self.display_name = data.get("display_name")
        self.display_name_normalized = data.get("display_name_normalized")
        self.fields = data.get("fields")
        self.status_text = data.get("status_text")
        self.status_emoji = data.get("status_emoji")
        self.status_emoji_display_info = data.get("status_emoji_display_info", [])
        self.status_expiration = data.get("status_expiration")
        self.avatar_hash = data.get("avatar_hash")
        self.huddle_state = data.get("huddle_state")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.image_24 = data.get("image_24")
        self.image_32 = data.get("image_32")
        self.image_48 = data.get("image_48")
        self.image_72 = data.get("image_72")
        self.image_192 = data.get("image_192")
        self.image_512 = data.get("image_512")
        self.status_text_canonical = data.get("status_text_canonical")
        team = data.get("team")
        self.team: Optional[Team] = state.teams[team] if team is not None else None


# It creates a class called User.
class Member:
    """This function takes in a UserPayload object and assigns it to the data attribute of the User class

    Attributes
    ----------
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

    bot: :class:`bool`
        Is bot.
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
        self.is_admin: bool = data.get("is_admin", False)
        self.is_owner: bool = data.get("is_owner")
        self.bot: bool = data.get("is_bot")
        self.is_app_user: bool = data.get("is_app_user")
        self.updated_at = datetime.fromtimestamp(float(data.get("updated", 0)))
        self.is_email_confirmed = data.get("is_email_confirmed")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    @property
    def mention(self) -> str:
        """Return member mention.

        Returns
        -------
        :class:`str`
            mention.
        """
        return f"<@{self.id}>"
