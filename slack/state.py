from __future__ import annotations

import asyncio
import datetime
import inspect
import logging
from typing import (
    Dict,
    Callable,
    Any,
    TYPE_CHECKING,
    Tuple,
    Set,
    Optional,
    TypeVar
)

from .channel import Channel, DeletedChannel
from .member import Member
from .message import (
    Message,
    JoinMessage,
    PurposeMessage,
    DeletedMessage,
    ArchivedMessage,
)
from .route import Route
from .team import Team

if TYPE_CHECKING:
    from .httpclient import HTTPClient

_logger = logging.getLogger(__name__)

Parsers = TypeVar("Parsers", bound=Dict[str, Callable[[Optional[Dict[str, Any]]], None]])


class ReactionEventType:
    """
    Attributes
    ----------
    type: :class:`str`
        Reaction type.

    reaction: :class:`str`
        Reaction name.

    file: :class:`Optional[str]`
        File ID(optional).

    file_comment: :class:`Optional[str]`
        File comment(optional).

    channel: :class:`~Channel`
        Channel data(optional).

    timestamp: :class:`datetime.datetime`
        Message created at.

    """
    def __init__(self, _type: str, state: "ConnectionState", payload: Dict[str, str]):
        self.type: str = _type
        self.reaction: str = ""
        self.file: Optional[str] = payload.get("file")
        self.file_comment: Optional[str] = payload.get("file_comment")
        self.channel: Optional[Channel] = state.channels.get(payload.get("channel", ""))
        self.timestamp: Optional[datetime.datetime] = datetime.datetime.fromtimestamp(float(payload.get("ts")))


class ConnectionState:
    """

    """

    def __init__(
            self,
            dispatch: Callable[..., None],
            http: HTTPClient,
            loop: asyncio.AbstractEventLoop,
            handlers: Dict[str, Callable],
            **kwargs
    ) -> None:
        self.http: HTTPClient = http
        self.loop: asyncio.AbstractEventLoop = loop
        self.dispatch: Callable[..., None] = dispatch
        self.handlers: Dict[str, Callable] = handlers
        self.all_events: Set[str] = set()
        parsers: Parsers
        self.parsers = parsers = {}
        self.teams: Dict[str, Team] = {}
        self.channels: Dict[str, Channel] = {}
        self.members: Dict[str, Member] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr[6:]] = func

    async def initialize(self) -> Tuple[
        Dict[str, Team],
        Dict[str, Channel],
        Dict[str, Member]
    ]:
        teams: Dict[str, Any] = await self.http.request(
            Route("GET", "auth.teams.list", self.http.bot_token)
        )
        for team in teams["teams"]:
            team_id = team["id"]
            info = await self.http.request(
                Route("GET", "team.info", self.http.bot_token),
                data={
                    "team": team_id
                }
            )
            self.teams[team_id] = Team(state=self, data=info["team"])
        await asyncio.sleep(0.2)
        for team in teams["teams"]:
            team_id = team["id"]
            channels: Dict[str, Any] = await self.http.request(
                Route("GET", "conversations.list", self.http.bot_token),
                data={
                    "team": team_id
                }
            )
            self.channels = {ch["id"]: Channel(state=self, data=ch) for ch in channels["channels"]}

        members: Dict[str, Any] = await self.http.request(
            Route("GET", "users.list", self.http.bot_token)
        )
        for member in members["members"]:
            self.members[member["id"]] = Member(state=self, data=member)

        return self.teams, self.channels, self.members

    def parse_hello(self, *args, **kwargs):
        self.all_events.add("on_ready")
        self.dispatch("ready")

    def parse_message(self, payload: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload["event"]
        message = Message(state=self, data=event)
        self.all_events.add("on_message")
        self.dispatch("message", message)

    def parse_channel_created(self, payload: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a channel object

        Parameters
        ----------
        payload : Dict[str, Any]
            The raw payload from the websocket.

        """
        event = payload['event']
        ch_data = event['channel']
        channel = Channel(state=self, data=ch_data)
        self.all_events.add("on_channel_create")
        self.dispatch("channel_create", channel)

    def parse_channel_deleted(self, payload: Dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a channel object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        channel = DeletedChannel(state=self, data=event)
        self.all_events.add("on_channel_delete")
        self.dispatch("channel_delete", channel)

    def parse_channel_purpose(self, payload: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : Dict[str, Any]
            The raw payload from the server.

        """
        event = payload['event']
        message = PurposeMessage(state=self, data=event)
        self.all_events.add("on_channel_purpose")
        self.dispatch("channel_purpose", message)

    def parse_message_deleted(self, payload: Dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a message object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = DeletedMessage(state=self, data=event)
        self.all_events.add("on_message_delete")
        self.dispatch("message_delete", message)

    def parse_channel_joined(self, payload: Dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a JoinMessage object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = JoinMessage(state=self, data=event)
        self.all_events.add("on_channel_join")
        self.dispatch("channel_join", message)

    def parse_channel_archive(self, payload: Dict[str, Any]) -> None:
        """This function takes a payload (a dictionary) and returns a message (an object)

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = ArchivedMessage(state=self, data=event)
        self.all_events.add("on_channel_archive")
        self.dispatch("channel_archive", message)

    def parse_message_changed(self, payload: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        before_message = Message(state=self, data=event['previous_message'])
        after_message = Message(state=self, data=event['message'])
        self.all_events.add("on_message_update")
        self.dispatch("message_update", before_message, after_message)

    def parse_channel_rename(self, payload: Dict[str, Any]):
        event = payload["event"]
        channel_data = event["channel"]
        channel = self.channels[channel_data["id"]]
        _channel = channel
        _channel.name = channel_data["name"]
        self.all_events.add("on_channel_rename")
        self.dispatch("channel_rename", channel, _channel)

    def parse_channel_unarchive(self, payload: Dict[str, Any]):
        channel = self.channels[payload["channel"]]
        user = self.members[payload["user"]]
        self.all_events.add("on_channel_unarchive")
        self.dispatch("channel_unarchive", channel, user)

    def parse_member_joined_channel(self, payload: Dict[str, Any]):
        channel = self.channels[payload["channel"]]
        user = self.members[payload["user"]]
        inviter = self.members[payload["inviter"]]
        self.all_events.add("on_member_join")
        self.dispatch("member_join", channel, user, inviter)

    def parse_member_left_channel(self, payload: Dict[str, Any]):
        user = self.members[payload["user"]]
        channel = self.channels[payload["channel"]]
        self.all_events.add("on_member_left")
        self.dispatch("member_left", channel, user)

    def parse_reaction_added(self, payload: Dict[str, Any]):
        user: Member = self.members[payload.get("user", "")]
        _type: str = payload["item"]["type"]
        item_user: Member = self.members.get(payload.get("item_user", ""))

        react_type = ReactionEventType(_type, self, payload["item"])
        react_type.reaction = payload["reaction"]

        self.all_events.add("on_reaction_add")
        self.dispatch("reaction_add", user, item_user, react_type)

    def parse_reaction_removed(self, payload: Dict[str, Any]):

        user: Member = self.members[payload.get("user", "")]
        _type: str = payload["item"]["type"]
        item_user: Member = self.members.get(payload.get("item_user", ""))

        react_type = ReactionEventType(_type, self, payload["item"])
        react_type.reaction = payload["reaction"]

        self.all_events.add("on_reaction_remove")
        self.dispatch("reaction_remove", user, item_user, react_type)

    def parse_pin_added(self, payload: Dict[str, Any]):
        self.all_events.add("pin_add")
        self.dispatch("pin_add")

    def parse_pin_removed(self, payload: Dict[str, Any]):
        self.all_events.add("pin_remove")
        self.dispatch("pin_remove")
