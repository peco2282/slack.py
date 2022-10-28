from __future__ import annotations

import asyncio
from typing import Any, Dict, TYPE_CHECKING, Optional, Union

import aiohttp

from .route import Route

if TYPE_CHECKING:
    from .ws import SlackWebSocket


class SlackException(Exception):
    pass


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
        self.__session: aiohttp.ClientSession = None
        self.ws: SlackWebSocket = None

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
            data: Optional[Dict[str, Any]] = None
    ) -> Union[
        Dict[str, Any],
        str
    ]:
        """request with param

        Parameters
        ----------
        route : Route
        data : Optional[Dict[str, Any]]

        Returns
        -------
            Union[Dict[str, Any], str]
        """
        headers = {
            "Authorization": f"Bearer {route.token}",
            "X-Slack-No-Retry": "1"
        }
        params = {
            "headers": headers
        }
        if data is not None:
            params["data"] = data

        method = route.method
        url = route.url

        async with self.__session.request(method, url, **params) as response:
            try:
                return await response.json()

            except:
                return await response.text()

    def send_message(self, route: Route, param):
        """It takes a parameter, and returns a request

        Parameters
        ----------
        route
            a data to request.
        param
            a dictionary of parameters to send to the Slack API.

        Returns
        -------
            The return value is a dictionary.

        """
        return self.request(
            route,
            param
        )

    def delete_message(self, route: Route, param):
        """This function deletes a message from a chat

        Parameters
        ----------
        route
            a data to connect.

        param
            keyword of send message.

        Returns
        -------
            The return value is the response from the request.

        """
        return self.request(
            route,
            param
        )

    def create_channel(self, route: Route, param):
        return self.request(
            route,
            param
        )

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
