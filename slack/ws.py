from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Dict, Any, Callable, List, Optional, Coroutine

import aiohttp

if TYPE_CHECKING:
    from .client import Client

_logger = logging.getLogger(__name__)


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
        self._slack_parsers: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self.socket = socket
        self.loop = loop
        # self.http = http
        self.logger: logging.Logger

        self.token: Optional[str]

        self._dispatch = lambda *args: None
        self._dispatch_listeners: List[Any] = []

    @classmethod
    async def from_client(cls, client: Client, ws_url: str, logger: logging.Logger) -> SlackWebSocket:
        """`from_client` is a class method that takes a `Client` object and a websocket URL and returns a
        `SlackWebSocket` object

        Parameters
        ----------
        cls
            The class that is being instantiated.
        client : Client
            The client object that you're using to connect to Slack.
        ws_url
            The URL to connect to.
        logger : logging.Logger

        Returns
        -------
            A SlackWebSocket object

        """
        socket = await client.http.ws_connect(ws_url)
        ws: SlackWebSocket = cls(socket=socket, loop=client.loop)
        ws.token = client.http.token
        ws.logger = logger

        ws._slack_parsers = client.connection.parsers
        await ws.poll_event()
        return ws

    async def poll_event(self) -> None:
        """It receives a message from the websocket, parses it, and then calls the appropriate function to handle the
        event

        """
        try:
            msg: aiohttp.WSMessage = await self.socket.receive()
            await self.parse_event(msg.json())

        except Exception as e:
            raise e

    async def response_event(self, envelope_id: str, payload: Dict[str, Any]):
        await asyncio.sleep(0.5)
        await self.socket.send_str(str({"envelope_id": envelope_id, "payload": json.dumps(payload)}))

    async def parse_event(self, data: Dict[str, Any]) -> None:
        """It takes a dictionary of data, and if the data is a hello event, it prints the data and sets the ready event.

        If the data is not a hello event, it gets the payload and event from the data, and sets the event type to the
        event subtype if the event is not None, and if the event type is None, it sets the event type to the event
        type.

        If the data retry reason is timeout, it returns.

        It then tries to get the function from the slack parsers' dictionary, and if it can't, it prints the payload
        and the event type.

        If it can get the function, it prints the function name and calls the function with the payload.

        It then creates an empty list, and for each index and entry in the dispatch listeners, it gets the future
        from the entry, and if the future is cancelled, it appends the index to the list

        Parameters
        ----------
        data : Dict[str, Any]
            Dict[str, Any]

        Returns
        -------
            The future object is being returned.

        """
        if data.get("type") == "hello":
            try:
                hello_func: Callable[..., Coroutine[Any, Any, Any]] = self._slack_parsers["hello"]

            except KeyError:
                pass

            else:
                hello_func()

        else:
            # if not data.get("ok") or data.get("ok") is None:
            #     return
            payload: Dict[str, Any] = data["payload"]
            event: Optional[Dict[str, Any]] = payload.get("event")
            event_type: Optional[str] = event.get("subtype") if event is not None else None
            await self.response_event(data["envelope_id"], data)
            if event is None:
                event_type = payload.get("type")

            if (event_type is None) and (event is not None):
                event_type = event.get("type")
            if data.get("retry_reason") == "timeout":
                return

            try:
                event_func: Callable[..., Coroutine[Any, Any, Any]] = self._slack_parsers[event_type]

            except KeyError:
                _logger.info("%s is not defined. (Undefined Event.)", event_type)
                pass

            else:
                event_func(payload)
                _logger.info(f"{event_type} function occuring.")

            removed = []
            for index, entry in enumerate(self._dispatch_listeners):

                future: asyncio.Future = entry.future
                if future.cancelled():
                    removed.append(index)
                    continue
