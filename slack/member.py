from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .channel import Channel
from .route import Route
from .team import Team
from .types.member import (
    Member as MemberPayload,
    Profile as ProfilePayload
)
from .message import Message

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
        self.__state = state
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
        __team = data.get("team")
        self.team: Team | None = state.teams[__team] if __team is not None else None


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
        self.__state = state
        self.id = data.get("id")
        self.team = state.teams[data.get("team_id")]
        self.deleted = data.get("deleted", False)
        self.color = data.get("color")
        self.real_name = data.get("real_name")
        self.tz = data.get("tz")
        self.tz_label = data.get("tz_label")
        self.tz_offset = data.get("tz_offset")
        self.profile: Profile = Profile(state, self, data.get("profile", {}))
        self.name = data.get("name")
        self.is_admin: bool = data.get("is_admin", False)
        self.is_owner: bool = data.get("is_owner", False)
        self.bot: bool = data.get("is_bot", False)
        self.is_app_user: bool = data.get("is_app_user", False)
        self.updated_at = datetime.fromtimestamp(float(data.get("updated", 0)))
        self.is_email_confirmed: bool = data.get("is_email_confirmed", False)

    def __eq__(self, other) -> bool:
        if isinstance(other, Member):
            return self.id == other.id

        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} is_bot={self.bot}>"

    @property
    def mention(self) -> str:
        """Return member mention.

        Returns
        -------
        :class:`str`
            mention.
        """
        return f"<@{self.id}>"

    async def send_dm(self, text: str):
        """

        .. versionadded:: 1.4.2

        Parameters
        ----------
        text: :class:`str`
            Message you want as DM.

        Returns
        -------
        :class:`Message`

        """
        rtn = await self.__state.http.send_message(
            Route("POST", "chat.postMessage", self.__state.http.bot_token),
            data={
                "channel": self.id,
                "text": str(text)
            }
        )
        return Message(self.__state, rtn.get("message"))

    async def kick(self, channel: Channel):
        """
        A way to :class:`Channel`.kick()

        Kick a member out of the channel.

        ..versionadded:: 1.4.5

        Parameters
        ----------
        channel: :class:`Channel`
            Channel you want to kick.
        """
        query = {
            "user": self.id,
            "channel": channel.id
        }
        await self.__state.http.post_anything(
            Route("POST", "conversations.kick", self.__state.http.bot_token),
            query=query
        )
