import asyncio
import inspect
import logging
from typing import Dict, Callable, Any

from . import (
    HTTPClient,
    Message,
    Channel,
    JoinMessage,
    PurposeMessage,
    DeletedMessage,
    DeletedChannel,
    ArchivedMessage,
    Route,
    Team,
    Member
)

_logger = logging.getLogger(__name__)


class ConnectionState:
    _parsers: Dict[str, Callable[[Dict[str, Any]], None]]

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
        parsers: Dict[str, Callable]
        self.parsers = parsers = {}
        self.teams: Dict[str, Team] = {}
        self.channels: Dict[str, Channel] = {}
        self.members: Dict[str, Member] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr[6:]] = func

    async def initialize(self):
        teams = await self.http.request(
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

        for team in teams["teams"]:
            team_id = team["id"]
            channels = await self.http.request(
                Route("GET", "conversations.list", self.http.bot_token),
                data={
                    "team": team_id
                }
            )
            self.channels[team_id] = [Channel(self, ch) for ch in channels["channels"]]

        members = await self.http.request(
            Route("GET", "users.list", self.http.bot_token)
        )
        for member in members["members"]:
            self.members[member["id"]] = Member(member)

        return self.teams, self.channels, self.members

    def parse_hello(self, *args, **kwargs):
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
        self.dispatch("message_delete", message)

    def parse_channel_join(self, payload: Dict[str, Any]) -> None:
        """It takes a payload (a dictionary) and returns a JoinMessage object

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the event.

        """
        event = payload['event']
        message = JoinMessage(state=self, data=event)
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
        self.dispatch("message_update", before_message, after_message)
