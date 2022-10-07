from __future__ import annotations

import asyncio
from typing import Any, Dict, TYPE_CHECKING, List, Optional, Union

import aiohttp

from . import Route

if TYPE_CHECKING:
    from . import SlackWebSocket


class SlackException(Exception):
    pass


class HTTPClient:
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            user_token: str,
            token: str,
            bot_token: str
    ):
        """connector of slackAPI

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
        user_token : str
        token : str
        bot_token : str
        """
        self.loop: asyncio.AbstractEventLoop = loop
        self.user_token: str = user_token
        self.token: str = token
        self.bot_token: str = bot_token
        self.__session: aiohttp.ClientSession = None
        self.ws: SlackWebSocket = None
        self.teams: Dict[str, Any] = {
        }

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
            "Authorization": f"Bearer {route.token}"
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

    def send_message(self, param):
        """It takes a parameter, and returns a request

        Parameters
        ----------
        param
            a dictionary of parameters to send to the Slack API.

        Returns
        -------
            The return value is a dictionary.

        """
        return self.request(
            Route("POST", "chat.postMessage", self.bot_token),
            param
        )

    def delete_message(self, param):
        """This function deletes a message from a chat

        Parameters
        ----------
        param
            keyword of send message.

        Returns
        -------
            The return value is the response from the request.

        """
        return self.request(
            Route("POST", "chat.delete", self.user_token),
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
        await asyncio.sleep(0.5)
        _list = await self.request(
            Route("GET", "auth.teams.list", self.bot_token)
        )
        _teams: List[Dict[str, str]] = _list["teams"]
        print(_teams)
        if len(_teams) >= 1:
            for _id in _teams:
                _t = await self.request(
                    Route("GET", "team.info", self.bot_token),
                    data={
                        "team": _id["id"]
                    }
                )
                _k = _id["id"]
                self.teams[_k] = _t
                await asyncio.sleep(0.2)
            print(self.teams)
        return data

    async def close(self):
        """It closes the session

        """
        if self.__session:
            await self.__session.close()
