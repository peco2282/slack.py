from __future__ import annotations

from typing import TYPE_CHECKING

from .route import Route
from .types import (
    File as FilePayload,
    Share as SharePayload,
    PublicShare as PublicSharePayload
)
from .utils import ts2time

if TYPE_CHECKING:
    from .channel import Channel

    from .state import ConnectionState


class Attachment:
    def __init__(self, fp: str, name: str, title: str, initial_comment: str | None = None):
        self.fp = fp
        self.name = str(name)
        self.title = str(title)
        self.initial_comment = str(initial_comment) if isinstance(initial_comment, str) else None


class PublicShare:
    def __init__(self, state: ConnectionState, data: PublicSharePayload):
        self.state = state
        self.reply_users: list[str | None] = data.get("reply_users", [])
        self.reply_users_count: int = data.get("reply_users_count", 0)
        self.reply_count: int = data.get("reply_count", 0)
        self.ts: str = data["ts"]
        self.channel_name: str = data["channel_name"]
        self.team_id: str = data["team_id"]
        self.share_user_id: str = data["share_user_id"]


class Share:
    def __init__(self, state: ConnectionState, data: SharePayload):
        self.state = state
        self.__share: dict[str, list[PublicSharePayload]] = data.get("public", {})
        self.publics: dict[str, list[PublicShare]] = {
            k: [PublicShare(state, c) for c in v] for k, v in self.__share.items()
        }

    def public(self, channel_id: str) -> list[PublicShare] | None:
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
        self.external_type: str | None = data.get("external_type")
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
        self.comments_count: str | None = data.get("comments_count")
        self.is_starred: bool = data.get("is_starred", False)
        self.shares: Share = Share(state, data.get("shares", {}))

        self.channels: list[Channel | None] = [self.state.channels.get(c) for c in data.get("channels", [])]
        self.groups: list[str | None] = data.get("groups", [])
        self.ims: list[str | None] = data.get("ims", [])
        self.has_rich_preview: bool = data.get("has_rich_preview", False)
        self.file_access: str | None = data.get("file_access")

    async def create_url(self):
        await self.state.http.get_anything(
            Route("GET", "files.getUploadURLExternal", self.state.http.bot_token),
            query={
                "filename": self.id,
                # "length": length
            }
        )
