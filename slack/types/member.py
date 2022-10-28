from typing import TypedDict, Dict, Any, List, Optional


class Profile(TypedDict):
    title: str
    phone: str
    skype: str
    real_name: str
    real_name_normalized: str
    display_name: str
    display_name_normalized: str
    fields: Optional[Dict[str, Any]]
    status_text: str
    status_emoji: str
    status_emoji_display_info: List[Any]
    status_expiration: int
    avatar_hash: str
    huddle_state: str
    always_active: bool
    first_name: str
    last_name: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    status_text_canonical: str
    team: str


class Member(TypedDict):
    id: str
    team_id: str
    name: str
    deleted: bool
    color: str
    real_name: str
    tz: str
    tz_label: str
    tz_offset: int
    profile: Profile
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    is_app_user: bool
    updated: int
    is_email_confirmed: bool
    who_can_share_contact_card: str
