from typing import TypedDict


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


class DeletedChannel(TypedDict):
    channel: str
    actor_id: str
    type: str
    event_ts: str
