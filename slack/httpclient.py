from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, TYPE_CHECKING, Optional, Union

import aiohttp

from .errors import RateLimitException
from .route import Route
from .utils import parse_exception

if TYPE_CHECKING:
    from .ws import SlackWebSocket


class HTTPClient:
    """connector of slackAPI

    Attributes
    ----------
    loop : asyncio.AbstractEventLoop
    user_token : str
    token : str
    bot_token : str

    """

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            user_token: str,
            token: str,
            bot_token: str
    ):
        self.loop: asyncio.AbstractEventLoop = loop
        self.user_token: str = user_token
        self.token: str = token
        self.bot_token: str = bot_token
        self.__session: Optional[aiohttp.ClientSession] = None
        self.ws: SlackWebSocket

    async def ws_connect(self, url: str):
        """It connects to a websocket and returns a websocket object

        Parameters
        ----------
        url : str
            he URL to connect to.

        Returns
        -------
            A websocket connection object.

        """
        return await self.__session.ws_connect(url=url)

    async def request(
            self,
            route: Route,
            data: Optional[Dict[str, Any]] = None,
            query: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Union[
        Dict[str, Any],
        str
    ]:
        """request with param

        Parameters
        ----------
        query
        route : Route
        data : Optional[Dict[str, Any]]

        Returns
        -------
            Union[Dict[str, Any], str]
        """
        headers = {
            "Authorization": f"Bearer {route.token}",
        }
        attrs = {
            "headers": headers
        }
        if data is not None:
            attrs["data"] = data

        if query is not None:
            query_url = "&".join(f"{k}={v}" for k, v in query.items())
            route.url += f"?{query_url}"

        method = route.method

        url = route.url

        async with self.__session.request(method, url, **attrs) as response:
            try:
                _json = await response.json()
                is_ok = _json.get("ok")
                if is_ok is True:
                    return _json

                else:
                    if _json.get("error") == "ratelimited":
                        raise RateLimitException(_json)

                    else:
                        parse_exception(_json["error"])

            except json.JSONDecodeError:
                return await response.text()

    def send_message(self, route: Route, data=None, query=None):
        """It takes a parameter, and returns a request

        Parameters
        ----------
        query
        data
        route
            a data to request.

        Returns
        -------
            The return value is a dictionary.

        """
        return self.request(
            route,
            data=data,
            query=query
        )

    def delete_message(self, route: Route, data):
        """This function deletes a message from a chat

        Parameters
        ----------
        route
            a data to connect.

        data
            keyword of send message.

        Returns
        -------
            The return value is the response from the request.

        """
        return self.request(
            route,
            data=data
        )

    def create_channel(self, route: Route, data):
        return self.request(
            route,
            data=data
        )

    def join_channel(self, route: Route, data):
        return self.request(route, data=data)

    async def login(self):
        """It gets a list of teams the bot is on, then gets the info for each team and stores it in a dictionary

        Returns
        -------
            The data that is being returned is the data that is being sent to the server.

        """
        self.__session = aiohttp.ClientSession()
        data = await self.request(
            Route("POST", "apps.connections.open", self.token)
        )
        return data

    async def close(self):
        """It closes the session

        """
        if self.__session:
            await self.__session.close()
