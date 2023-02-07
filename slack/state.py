# from __future__ import annotations
from __future__ import annotations

import asyncio
import datetime
import inspect
import logging
import sys
from typing import (
    Callable,
    Any,
    TYPE_CHECKING,
    TypeVar,
    Generic,
    Optional,
)

from typing_extensions import Unpack

from .block import Block
from .channel import Channel, DeletedChannel
from .member import Member
from .message import (
    Message,
    JoinMessage,
    PurposeMessage,
    DeletedMessage,
)
from .route import Route
from .team import Team
from .utils import ts2time

if TYPE_CHECKING:
    from .httpclient import HTTPClient

_logger = logging.getLogger(__name__)

Parsers = TypeVar("Parsers", bound=dict[str, Callable[[Optional[dict[str, Any]]], None]])

if sys.version_info >= (3, 11,):
    # noinspection PyCompatibility
    Dispatch = TypeVar("Dispatch", bound=Callable[[str, *tuple[str, ...] | None], str])

else:
    Dispatch = TypeVar("Dispatch", bound=Callable[[str, Unpack[tuple[str, ...]] | None], None])


class ReactionEvent:
    """
    Attributes
    ----------
    type: :class:`str`
        Reaction type.

    reaction: :class:`str`
        Reaction name.

    file: Optional[:class:`str`]
        Attachment ID(optional).

    file_comment: Optional[:class:`str`]
        Attachment comment(optional).

    channel: :class:`Channel`
        Channel data(optional).

    timestamp: :class:`datetime.datetime`
        Reaction added at.

    message_timestamp: :class:`datetime.datetime`
        Message of reaction added timestamp.

    """

    def __init__(self, _type: str, state: "ConnectionState", event: dict[str, Any]):
        self.type: str = _type
        self.reaction: str = event.get("reaction")
        self.file: str | None = event.get("item", {}).get("file")
        self.file_comment: str | None = event.get("file_comment")
        self.channel: Channel | None = state.channels.get(event.get("item", {}).get("channel", ""))
        self.timestamp: datetime.datetime | None = datetime.datetime.fromtimestamp(
            float(event.get("item", {}).get("ts", 0)))
        self.message_timestamp: datetime.datetime | None = ts2time(event.get("event_ts", 0))


class ConnectionState:
    # noinspection PyUnusedLocal
    def __init__(
            self,
            dispatch: Dispatch,
            http: HTTPClient,
            loop: asyncio.AbstractEventLoop,
            handlers: dict[str, Callable[[], None]],
            **kwargs
    ) -> None:
        self.http: HTTPClient = http
        self.loop: asyncio.AbstractEventLoop = loop
        self.dispatch: Dispatch = dispatch
        self.handlers: dict[str, Callable[[], None]] = handlers
        self.all_events: set[str] = set()
        parsers: Generic[Parsers]
        self.parsers = parsers = {}
        self.teams: dict[str, Team] = {}
        self.channels: dict[str, Channel] = {}
        self.members: dict[str, Member] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr[6:]] = func

    async def initialize(self) -> tuple[
        dict[str, Team],
        dict[str, Channel],
        dict[str, Member]
    ]:
        # Request installed team ids.
        teams: dict[str, Any] = await self.http.request(
            Route("GET", "auth.teams.list", self.http.bot_token)
        )
        await asyncio.sleep(0.5)

        # Request team data.
        team_tasks = []
        for team in teams["teams"]:
            team_id = team["id"]
            team_tasks.append(
                asyncio.ensure_future(
                    self.http.request(
                        Route("GET", "team.info", self.http.bot_token),
                        data={"team": team_id}
                    )
                )
            )
        _teams = await asyncio.gather(*team_tasks, return_exceptions=True)

        # Serialize Team class.
        for team in _teams:
            self.teams[team["team"]["id"]] = Team(self, team)

        await asyncio.sleep(0.5)

        # Request channel data from team id.
        channel_tasks = []
        for team in teams["teams"]:
            team_id = team["id"]
            channel_tasks.append(
                asyncio.ensure_future(
                    self.http.request(
                        Route("GET", "conversations.list", self.http.bot_token),
                        data={"team": team_id}
                    )
                )
            )
        _channels = await asyncio.gather(*channel_tasks, return_exceptions=True)
        # Selialize Channel class.
        for chs in _channels:
            for ch in chs["channels"]:
                self.channels[ch["id"]] = Channel(self, ch)

        await asyncio.sleep(0.5)

        while True:
            try:
                # Request member data.
                members: dict[str, Any] = await self.http.request(
                    Route("GET", "users.list", self.http.bot_token)
                )
                # Serialize Member class.
                for member in members["members"]:
                    self.members[member["id"]] = Member(state=self, data=member)

            except AttributeError:
                continue

            else:
                break

        return self.teams, self.channels, self.members

    # noinspection PyUnusedLocal
    def parse_hello(self, *args, **kwargs):
        self.dispatch("ready")

    def parse_message(self, payload: dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        event = payload["event"]
        message = Message(state=self, data=event)
        self.all_events.add("on_message")
        self.dispatch("message", message)

    def parse_channel_created(self, payload: dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a channel object

        Parameters
        ----------
        payload : dict[str, Any]
            The raw payload from the websocket.

        """
        event = payload['event']
        ch_data = event['channel']
        channel = Channel(state=self, data=ch_data)
        self.all_events.add("on_channel_create")
        self.channels[channel.id] = channel
        self.dispatch("channel_create", channel)

    def parse_channel_deleted(self, payload: dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a channel object

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        channel = DeletedChannel(state=self, data=event)
        del self.channels[channel.channel_id]
        self.all_events.add("on_channel_delete")
        self.dispatch("channel_delete", channel)

    def parse_channel_purpose(self, payload: dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : dict[str, Any]
            The raw payload from the server.

        """
        event = payload['event']
        message = PurposeMessage(state=self, data=event)
        self.all_events.add("on_channel_purpose")
        self.dispatch("channel_purpose", message)

    def parse_message_deleted(self, payload: dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a message object

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = DeletedMessage(state=self, data=event)
        self.all_events.add("on_message_delete")
        self.dispatch("message_delete", message)

    def parse_channel_joined(self, payload: dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a JoinMessage object

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = JoinMessage(state=self, data=event)
        self.all_events.add("on_channel_join")
        self.dispatch("channel_join", message)

    def parse_app_mention(self, payload: dict[str, Any]):
        event = payload['event']
        message = Message(self, event)
        message.team_id = payload.get("team")
        self.dispatch("mention", message)

    def parse_channel_archive(self, payload: dict[str, Any]) -> None:
        """This function takes a payload (a dictionary) and returns a message (an object)

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        # event = payload['event']
        # message = ArchivedMessage(state=self, data=event)
        # self.all_events.add("on_channel_archive")
        # self.dispatch("channel_archive", message)
        ...

    def parse_team_rename(self, payload: dict[str, Any]) -> None:
        # event = payload['event']
        self.all_events.add("on_team_rename")

    def parse_message_changed(self, payload: dict[str, Any]) -> None:
        """It takes a dictionary of data, and returns a message object

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        before_message = Message(state=self, data=event['previous_message'])
        after_message = Message(state=self, data=event['message'])
        self.all_events.add("on_message_update")
        self.dispatch("message_update", before_message, after_message)

    def parse_channel_rename(self, payload: dict[str, Any]):
        event = payload["event"]
        channel_data = event["channel"]
        channel = self.channels[channel_data["id"]]
        _channel = channel
        _channel.name = channel_data["name"]
        self.all_events.add("on_channel_rename")
        self.dispatch("channel_rename", channel, _channel)

    def parse_channel_unarchive(self, payload: dict[str, Any]):
        event = payload["event"]
        channel = self.channels[event["channel"]]
        user = self.members[event["user"]]
        self.all_events.add("on_channel_unarchive")
        self.dispatch("channel_unarchive", channel, user)

    def parse_member_joined_channel(self, payload: dict[str, Any]):
        event = payload["event"]
        channel = self.channels[event["channel"]]
        user = self.members[event["user"]]
        inviter = self.members[event["inviter"]]
        self.all_events.add("on_member_join")
        self.dispatch("member_join", channel, user, inviter)

    def parse_member_left_channel(self, payload: dict[str, Any]):
        event = payload["event"]
        user = self.members[event["user"]]
        channel = self.channels[event["channel"]]
        self.all_events.add("on_member_left")
        self.dispatch("member_left", channel, user)

    def parse_reaction_added(self, payload: dict[str, Any]):
        event = payload['event']
        user: Member = self.members[event["user"]]
        _type: str = event["item"]["type"]
        item_user: Member = self.members[event["item_user"]]

        react_type = ReactionEvent(_type, self, event)

        self.dispatch("reaction_added", user, item_user, react_type)

    def parse_reaction_removed(self, payload: dict[str, Any]):
        event = payload.get("event", {})
        user: Member = self.members[event["user"]]
        _type: str = event["item"]["type"]
        item_user: Member = self.members[event["item_user"]]

        react_type = ReactionEvent(_type, self, event)

        self.all_events.add("on_reaction_remove")
        self.dispatch("reaction_removed", user, item_user, react_type)

    def parse_pin_added(self, payload: dict[str, Any]):
        payload.get("event", {})
        self.all_events.add("pin_add")
        self.dispatch("pin_add")

    def parse_pin_removed(self, payload: dict[str, Any]):
        payload.get("event", {})
        self.all_events.add("pin_remove")
        self.dispatch("pin_remove")

    def parse_block_actions(self, payload: dict[str, Any]):
        block = Block(self, payload)
        self.dispatch("block_action", block)

    def parse_file_change(self, payload: dict[str, Any]):
        event = payload.get("event", {})
        file_id = event.get("file_id")
        # file = self.http.get_anything(Route())
        user = self.members.get(event.get("user_id", ""))
        team = self.teams.get(payload.get("team_id", ""))
        self.dispatch("file_update")

    def parse_app_home_opened(self, payload: dict[str, Any]):
        event = payload.get("event", {})
        user = self.members.get(event.get("user", ""))
        ts = event.get("ts")

    def parse_thread_broadcast(self, payload: dict[str, Any]):
        event = payload.get("event", {})
        user = self.members.get(event.get("user", ""))
