from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Dict, Any, Callable, List

import aiohttp

if TYPE_CHECKING:
    from . import Client


class SlackWebSocket:
    def __init__(
            self,
            socket: aiohttp.ClientWebSocketResponse,
            loop: asyncio.AbstractEventLoop,
    ) -> None:
        """Websocket with client loop.

        Parameters
        ----------
        socket : aiohttp.ClientWebSocketResponse
            response of websocket.
        loop : asyncio.AbstractEventLoop
            Slackbot loop.
        """
        self._slack_parsers: List[Callable] = []
        self.socket = socket
        self.loop = loop
        # self.http = http

        self._dispatch = lambda *args: None
        self._dispatch_listeners = []

    @classmethod
    async def from_client(cls, client: Client, ws_url) -> SlackWebSocket:
        """`from_client` is a class method that takes a `Client` object and a websocket URL and returns a `SlackWebSocket`
        object

        Parameters
        ----------
        cls
            The class that is being instantiated.
        client : Client
            The client object that you're using to connect to Slack.
        ws_url
            The URL to connect to.

        Returns
        -------
            A SlackWebSocket object

        """
        socket = await client.http.ws_connect(ws_url)
        ws: SlackWebSocket = cls(socket=socket, loop=client.loop)
        ws.token = client.http.token

        ws._slack_parsers = client.connection.parsers
        await ws.poll_event()
        return ws

    async def poll_event(self) -> None:
        """It receives a message from the websocket, parses it, and then calls the appropriate function to handle the event

        """
        try:
            msg: aiohttp.WSMessage = await self.socket.receive()
            self.parse_event(json.loads(msg.data))

        except Exception as e:
            raise e

    def parse_event(self, data: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and if the data is a hello event, it prints the data and sets the ready event.

        If the data is not a hello event, it gets the payload and event from the data, and sets the event type to the event
        subtype if the event is not None, and if the event type is None, it sets the event type to the event type.

        If the data retry reason is timeout, it returns.

        It then tries to get the function from the slack parsers dictionary, and if it can't, it prints the payload and the
        event type.

        If it can get the function, it prints the function name and calls the function with the payload.

        It then creates an empty list, and for each index and entry in the dispatch listeners, it gets the future from the
        entry, and if the future is cancelled, it appends the index to the list

        Parameters
        ----------
        data : Dict[str, Any]
            Dict[str, Any]

        Returns
        -------
            The future object is being returned.

        """
        event_type: str = None
        if data.get("type") == "hello":
            print(data)
            self._slack_parsers["ready"] = data
            # TODO get team

        else:
            payload: Dict[str, Any] = data.get("payload")
            event: Dict[str, Any] = payload.get("event")
            event_type: str = event.get("subtype") if event is not None else "undefined event"
            print(event_type)
            if event_type is None:
                event_type = event.get("type")

            if data.get("retry_reason") == "timeout":
                return

            try:
                func: Callable = self._slack_parsers[event_type]
                print("func:", func.__name__)

            except KeyError as key:
                print("---")
                print(payload)
                print("---")
                print(f"{event_type} is not defined")

            else:
                func(payload)

            removed = []
            for index, entry in enumerate(self._dispatch_listeners):
                future = entry.future
                if future.cancelled():
                    removed.append(index)
                    continue
