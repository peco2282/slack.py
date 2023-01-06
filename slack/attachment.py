from typing import List, Optional, Dict

from . import Channel
from .state import ConnectionState
from .types import (
    File as FilePayload,
    Share as SharePayload,
    PublicShare as PublicSharePayload
)
from .utils import ts2time


class Attachment:
    def __init__(self, fp: str, name: str, title: str, initial_comment: str = None):
        self.fp = fp
        self.name = str(name)
        self.title = str(title)
        self.initial_comment = str(initial_comment)


class PublicShare:
    def __init__(self, state: ConnectionState, data: PublicSharePayload):
        self.state = state
        self.reply_users: List[str] = data.get("reply_users")
        self.reply_users_count: int = data.get("reply_users_count")
        self.reply_count: int = data.get("reply_count")
        self.ts: str = data.get("ts")
        self.channel_name: str = data.get("channel_name")
        self.team_id: str = data.get("team_id")
        self.share_user_id: str = data.get("share_user_id")


class Share:
    def __init__(self, state: ConnectionState, data: SharePayload):
        self.state = state
        self.__share: Dict[str, List[PublicSharePayload]] = data.get("public")
        self.publics: Dict[str, List[PublicShare]] = {
            k: [PublicShare(state, c) for c in v] for k, v in self.__share.items()
        }

    def public(self, channel_id: str) -> Optional[PublicShare]:
        return self.publics.get(channel_id)


class File:
    def __init__(self, state: ConnectionState, data: FilePayload):
        self.state = state
        self.id = data["id"]
        self.created_at = ts2time(data["created"])
        self.name = data["name"]
        self.title = data["title"]
        self.mimetype = data["mimetype"]
        self.filetype = data["filetype"]
        self.pretty_type = data.get("pretty_type")
        self.user = self.state.members.get(data.get("user", ""))
        self.team = self.state.teams.get(data.get("user_team", ""))
        self.is_editable = data.get("editable", False)
        self.size = int(data.get("size", 0))
        self.mode = data.get("mode")
        self.is_external = data.get("is_external")
        self.external_type: Optional[str] = data.get("external_type")
        self.is_public: bool = data.get("is_public", False)
        self.public_url_shared: bool = data.get("public_url_shared", False)
        self.display_as_bot: bool = data.get("display_as_bot", False)
        self.username: str = data["username"]
        self.url_private: str = data["url_private"]
        self.url_private_download: str = data["url_private_download"]
        self.permalink: str = data["permalink"]
        self.permalink_public: str = data["permalink_public"]
        self.edit_link: str = data["edit_link"]
        self.preview: str = data["preview"]
        self.preview_highlight: str = data["preview_highlight"]
        self.lines: int = data.get("lines", 0)
        self.lines_more: int = data.get("lines_more", 0)
        self.preview_is_truncated: bool = data.get("preview_is_truncated", False)
        self.comments_count: Optional[str] = data.get("comments_count")
        self.is_starred: bool = data.get("is_starred", False)
        self.shares: Share = Share(state, data.get("shares", {}))

        self.channels: List[Optional[Channel]] = [self.state.channels.get(c) for c in data.get("channels", [])]
        self.groups: List[Optional[str]] = data.get("groups")
        self.ims: List[Optional[str]] = data.get("ims")
        self.has_rich_preview: bool = data.get("has_rich_preview")
        self.file_access: str = data.get("file_access")

