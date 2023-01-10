from __future__ import annotations

import asyncio
import json
import traceback
from typing import Any, Dict, TYPE_CHECKING, Optional, Union, List, IO

import aiohttp

from .attachment import Attachment
from .errors import RateLimitException, ForbiddenException
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
            token: Optional[str],
            bot_token: str
    ):
        self.loop: asyncio.AbstractEventLoop = loop
        self.user_token: str = user_token
        self.token: Optional[str] = token
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
        is_file = False
        f: Optional[IO] = None
        files: Optional[List[Attachment]] = kwargs.get("files")
        if files is not None:
            f = open(files[0].fp, mode="rb")
            data["file"] = f

        if data is not None:
            attrs["data"] = data

        if query is not None:
            query_url = "&".join(f"{k}={v}" for k, v in query.items())
            route.url += f"?{query_url}"

        method = route.method

        url = route.url

        async with self.__session.request(method, url, **attrs) as response:
            try:
                _json = await response.json(content_type=None)
                is_ok = _json.get("ok")
                if 300 > response.status >= 200:
                    if is_ok is True:
                        if is_file is True:
                            try:
                                f.close()

                            except IOError as io:
                                traceback.format_exception(io)
                                raise io

                            finally:
                                is_file = False
                        return _json

                    else:
                        if _json.get("error") == "ratelimited":

                            raise RateLimitException(_json)

                        else:
                            parse_exception(_json["error"])

                elif response.status == 403:
                    raise ForbiddenException()

            except json.JSONDecodeError:
                return await response.text()

    def send_files(self, route: Route, data: Any, file: Attachment = None, files: List[Attachment] = None):
        if file is not None:
            files = [file]

        return self.request(
            route,
            data=data,
            files=files,
        )

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

    def get_anything(self, route: Route, data):
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
