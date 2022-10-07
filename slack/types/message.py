from typing import TypedDict, Literal, Optional

mimetypes = Literal[
    "image/png",
    "text/plain",
    "application/pdf"
]

messagesubtype = Literal[
    "message_updated",
    "message_deleted"
]

__all__ = (
    "PreviousMessage",
    "DeletedMessage",
    "Attatchment",
    "Message",
    "JoinMessage",
    "PurposeMessage",
    "ArchivedMessage"
)


class ArchivedMessage(TypedDict):
    type: str
    subtype: messagesubtype
    ts: str
    user: str
    text: str
    channel: str
    event_ts: str
    channel_type: str


class PreviousMessage(TypedDict):
    client_msg_id: str
    type: str
    subtype: str
    text: str
    user: str
    ts: str
    team: str


class DeletedMessage(TypedDict):
    channel: str
    # actor_id: str
    type: str
    event_ts: str
    subtype: str
    previous_message: PreviousMessage
    ts: str
    hidden: bool
    deleted_ts: str
    channel_type: str


class Attatchment(TypedDict):
    # files
    id: str
    created: int
    timestamp: int
    name: str
    title: str
    mimetype: mimetypes
    filetype: str
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
    media_display_type: str
    thumb_64: str
    thumb_80: str
    thumb_360: str
    thumb_360_w: int
    thumb_360_h: int
    thumb_160: str
    original_w: int
    original_h: int
    thumb_tiny: str
    permalink: str
    edit_link: str
    preview: str
    preview_highlight: str
    preview_is_truncated: str
    lines: int
    lines_more: int
    permalink_public: str
    has_rich_preview: bool
    file_access: str


class Message(TypedDict):
    type: str
    text: str
    files: Optional[Attatchment]
    upload: bool
    user: str
    display_as_bot: bool
    ts: str
    client_msg_id: str
    channel: str
    team: str
    # subtype: str
    event_ts: str
    channel_type: str
    channel: str
    event_ts: str
    channel_type: str
    # blocks:

    edited_user: Optional[str]
    edited_ts: str


class JoinMessage(TypedDict):
    type: str
    subtype: str
    ts: str
    user: str
    text: str
    channel: str
    event_ts: str
    channel_type: str


class PurposeMessage(JoinMessage):
    purpose: str
