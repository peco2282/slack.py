from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from .channel import Channel
from .member import Member
from .message import Message
from .team import Team
from .types.block import (
    Block as BlockPayload,
    Action as ActionPayload
)

if TYPE_CHECKING:
    from .state import ConnectionState


class Action:
    """
    Contains data from the specific interactive component that was used. App surfaces can contain blocks with multiple
    interactive components, and each of those components can have multiple values selected by users.

    Attributes
    ----------
    block_id: :class:`str`
        Identifies the block within a surface that contained the interactive component that was used.

    action_id: :class:`str`
        Identifies the interactive component itself. Some blocks can contain multiple interactive
        components, so the block_id alone may not be specific enough to identify the source component.

    """

    def __init__(self, state: ConnectionState, data: ActionPayload):
        self.state = state
        self.data = data
        self.type = data.get("type")
        self.action_id = data.get("action_id")
        self.block_id = data.get("block_id")
        self.action_ts = data.get("action_ts")


# *|MARKER_CURSOR|*
class Block:
    """
    This class be called :func:`on_block_actions()` event.
    Different interactive components will cause an interaction payload to be sent at different moments.

    Attributes
    ----------
    member: :class:`Member`
        Member who returned a response.

    trigger_id: :class:`str`
        Eigenvalue for response.

    response_url: :class:`str`
        A short-lived webhook.

    actions: List[:class:`Action`]
        Contains data from the specific interactive component that was used. App surfaces can
        contain blocks with multiple interactive components, and each of those components can have multiple values
        selected by users.

    Examples
    --------
    This class be called only :func:`on_block_actions` event.

    ::

        @client.event
        async def on_block_actions(block):
            action = block.actions[0]
            if action.get("action_id") == "action":
                await block.channel.send("Action called!!")

            else:
                await block.channel.send("This is not `action` event")

    """

    def __init__(self, state: ConnectionState, data: BlockPayload):
        self.state = state
        self.__data = data
        self.member: Member = state.members.get(data.get("user", {}).get("id"))
        self.trigger_id = data.get("trigger_id")
        self.enterprise = data.get("enterprise")
        self.is_enterprise_install = data.get("is_enterprise_install", False)
        self.message: Message = Message(state, data.get("message"))
        self.response_url: str = data.get("response_url")
        self.actions: List[Action] = [
            Action(state, action)
            for action in data.get("actions")
        ]

    @property
    def channel(self) -> Optional[Channel]:
        """
        Returns
        -------
        Optional[:class:`Channel`]
            Return responsed channel
        """
        return self.state.channels.get(self.__data.get("channel", {}).get("id", ""))

    @property
    def team(self) -> Optional[Team]:
        """
        Returns
        -------
        Optional[:class:`Team`]
            Return responsed team.
        """
        return self.state.teams.get(self.__data.get("team", {}).get("id", ""))
