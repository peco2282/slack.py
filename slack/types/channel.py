from __future__ import annotations

from typing import TypedDict


class Serializable(TypedDict):
    value: str
    creator: str
    last_set: int


class Channel(TypedDict):
    id: str
    is_channel: bool
    name: str
    name_normalized: str
    created: str
    creator: str
    is_shared: bool
    is_org_shared: bool
    context_team_id: str
    purpose: Serializable
    is_im: bool
    is_mpim: bool
    is_private: bool
    is_archived: bool
    unlinked: int
    is_general: bool
    is_pending_ext_shared: bool
    updated: int
    parent_conversation: str | None
    shared_team_id: list[str]
    topic: Serializable
    previous_names: list[str | None]


class DeletedChannel(TypedDict):
    channel: str
    actor_id: str
    type: str
    event_ts: str
