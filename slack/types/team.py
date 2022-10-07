from typing import TypedDict


class Icon(TypedDict):
    image_default: bool
    image_34: str
    image_44: str
    image_68: str
    image_88: str
    image_102: str
    image_230: str
    image_132: str


class Team(TypedDict):
    id: str
    name: str
    url: str
    domain: str
    email_domain: str
    icon: Icon
    avatar_base_url: str
    is_verified: bool
