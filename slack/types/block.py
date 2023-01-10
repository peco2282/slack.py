from typing import TypedDict, Optional, Any, List, Dict


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
    user: Dict[str, str]
    container: Container
    trigger_id: str
    team: Dict[str, str]
    enterprise: Optional[Any]
    is_enterprise_install: bool
    channel: Dict[str, str]
    message: Dict[str, Any]
    state: Dict[str, Any]
    response_url: str
    actions: List[Action]
