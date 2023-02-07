from __future__ import annotations

from typing import TypedDict, Any


class Container(TypedDict):
    type: str
    message_ts: str
    channel_id: str
    is_ephemeral: bool


class Action(TypedDict):
    type: str
    action_id: str
    block_id: str
    selected_user: str
    action_ts: str


class Block(TypedDict):
    user: dict[str, str]
    container: Container
    trigger_id: str
    team: dict[str, str]
    enterprise: Any | None
    is_enterprise_install: bool
    channel: dict[str, str]
    message: dict[str, Any]
    state: dict[str, Any]
    response_url: str
    actions: dict[Action]
