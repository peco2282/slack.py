from __future__ import annotations

from typing import TypedDict, Literal
from .message import mimetypes

filetypes = Literal[
    "python",
]


class PublicShare(TypedDict):
    reply_users: list[str]
    reply_users_count: int
    reply_count: int
    ts: str
    channel_name: str
    team_id: str
    share_user_id: str


class Share(TypedDict):
    public: dict[str, list[PublicShare]]


class File(TypedDict):
    id: str
    created: int
    timestamp: int
    name: str
    title: str
    mimetype: mimetypes
    filetype: filetypes
    pretty_type: str
    user: str
    user_team: str
    editable: bool
    size: int
    mode: str
    is_external: bool
    external_type: str
    is_public: bool
    public_url_shared: bool
    display_as_bot: bool
    username: str
    url_private: str
    url_private_download: str
    permalink: str
    permalink_public: str
    edit_link: str
    preview: str
    preview_highlight: str
    lines: int
    lines_more: int
    preview_is_truncated: bool
    comments_count: str
    is_starred: bool
    shares: Share
    channels: list[str]
    groups: list[str | None]
    ims: list[str | None]
    has_rich_preview: bool
    file_access: str
