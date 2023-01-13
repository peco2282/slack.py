from __future__ import annotations

import json
import urllib.parse
from datetime import datetime
from typing import overload, Optional, List, Dict, Union, TYPE_CHECKING

import slack
from .errors import InvalidArgumentException
from .route import Route
from .utils import ts2time
from .view import ViewFrame

if TYPE_CHECKING:
    from .attachment import Attachment
    from .member import Member
    from .message import Message
    from .state import ConnectionState


class Sendable:
    state: ConnectionState
    id: str
    # channel_id

    @property
    def everyone(self) -> str:
        """
        .. versionadded:: 1.4.0

        Returns
        -------
        :class:`str`
        """
        return "<@everyone>"

    @property
    def here(self) -> str:
        """

        .. versionadded:: 1.4.0

        Returns
        -------
        :class:`str`
        """
        return "<@here>"

    @overload
    async def send(
            self,
            text: str = ...,
            as_user: bool = ...
    ):
        ...

    @overload
    async def send(
            self,
            view: ViewFrame = ...,
            as_user: bool = ...
    ):
        ...

    async def send(
            self,
            text: Optional[str] = None,
            view: Optional[ViewFrame] = None,
            as_user: bool = False
    ) -> Message:
        """|coro|

        It sends a message to a channel.

        .. versionchanged:: 1.4.0
            Add `view` parameter.

        Parameters
        ----------
        text : Optional[:class:`str`]
            The text of the message to send.

        view: Optional[:class:`ViewFrame`]
            The viewframe contain blocks of the message to send.

        as_user: :class:`str`
            Is message send by user or not.

            .. versionadded:: 1.4.2

        Raises
        ------
        :class:`InvalidArgumentException`
            Raise when text and view are in param.

        Returns
        -------
        :class:`Message`
            A Message object.

        """
        param = query = {}
        if (text is not None) and (view is not None):
            raise InvalidArgumentException()

        if text is not None:
            param = {
                "channel": self.id,
                "text": str(text)
            }

        if as_user:
            param["as_user"] = True

        if view is not None:
            if not issubclass(type(view), ViewFrame):
                raise InvalidArgumentException("")
            blocks = json.dumps(view.to_list())
            query = {
                "channel": self.id,
                "blocks": urllib.parse.quote(str(blocks)).replace("%25", "%").replace("%27", "%22")
            }
        query.update(param)
        message = await self.state.http.send_message(
            Route("POST", "chat.postMessage", token=self.state.http.bot_token),
            # data=param if param != {} else None,
            query=query if query != {} else None
        )
        msg = slack.Message(state=self.state, data=message["message"])
        msg.channel_id = self.id
        return msg

    async def send_schedule(
            self,
            text: str,
            date: Union[datetime, int, float]
    ) -> Message:
        """This function is sending scheduled message with UNIX timestamp.

        .. versionadded:: 1.4.2

        Parameters
        ----------
        text: :class:`str`
            Message content.

        date: Optional[:class:`datetime`,:class:`int`:class:`float`]
            Timestamp when scheduled message sending.

        Returns
        -------
        :class:`Message`
            Message object.
        """
        param = {
            "channel": self.id,
            "text": str(text)
        }
        if isinstance(date, datetime):
            param["post_at"] = int(date.timestamp())

        elif isinstance(date, (int, float)):
            param["post_at"] = int(date)

        else:
            raise InvalidArgumentException("`date` parameter must be `datetime`, `int` or `float`.")
        resp = await self.state.http.send_message(
            Route("POST", "chat.scheduleMessage", self.state.http.bot_token),
            data=param
        )
        message = Message(self.state, resp["message"])
        message.id = resp.get("post_at")
        message.channel_id = resp.get("channel")
        message.scheduled_message_id = resp.get("scheduled_message_id")
        return message

    async def get_scheduled_messages(
            self,
            limit: Optional[int] = None,
            latest: Optional[datetime, int, float] = None,
            oldest: Optional[datetime, int, float] = None
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Examples
        --------
        Examples ::

            async for message in channel.get_scheduled_messages():
                print(message.content)

        Parameters
        ----------
        limit
        latest
        oldest

        Returns
        -------

        """
        if any(
                [
                    isinstance(limit, (int, type(None))),
                    *[isinstance(
                        t, (datetime, int, float, type(None))
                    ) for t in [latest, oldest]]
                ]
        ):
            raise InvalidArgumentException()
        param = {
            "channel": self.id
        }
        if latest is not None and oldest is not None:
            if isinstance(latest, datetime):
                latest = latest.timestamp()

            if isinstance(oldest, datetime):
                oldest = oldest.timestamp()

            if oldest > latest:
                latest, oldest = oldest, latest

            param["latest"] = int(latest)
            param["oldest"] = int(oldest)

        elif latest is not None:
            if isinstance(latest, datetime):
                latest = latest.timestamp()

            param["latest"] = int(latest)

        elif oldest is not None:
            if isinstance(oldest, datetime):
                oldest = oldest.timestamp()

            param["oldest"] = int(oldest)
        rtn = await self.state.http.get_anything(
            Route("GET", "chat.scheduledMessages.list", self.state.http.bot_token),
            param
        )
        messages = [m for m in rtn.get("scheduled_messages", [])]
        return messages

    async def send_ephemeral(self, text: str, member: Member) -> datetime:
        """|coro|
        Send Ephemeral message.

        .. versionadded:: 1.4.0

        Parameters
        ----------
        text: :class:`str`
            The text of the message to send.

        member: :class:`Member`
            send member.

        Returns
        -------
        :class:`datetime`
            Message posted time.

        """

        if not isinstance(member, Member):
            raise InvalidArgumentException("`member` parameter must instance `Member` class")

        param = {
            "channel": self.id,
            "text": str(text),
            "user": member.id
        }
        rtn = await self.state.http.send_message(
            Route(method="POST", endpoint="chat.postEphemeral", token=self.state.http.bot_token),
            data=param
        )

        return ts2time(rtn.get("message_ts", "0"))

    async def send_file(self, attachment: Attachment) -> slack.File:
        """This function occur sending file.

        Parameters
        ----------
        attachment: :class:`Attachment`
            Your file to send.

        Returns
        -------
        :class:`File`
            Sended data of file.
        """
        initial_text = attachment.initial_comment

        param = {
            "channels": self.id,
            "title": attachment.title,
            "filename": attachment.name
        }
        if initial_text:
            param["initial_comment"] = initial_text

        sended = await self.state.http.send_files(
            Route(method="POST", endpoint="files.upload", token=self.state.http.bot_token),
            data=param,
            files=[attachment],
        )
        return slack.File(self.state, sended["file"])

    async def get_permalink(self, message: Message):
        if not isinstance(message, Message):
            raise InvalidArgumentException("`message` parameter must instance `Message` class")
        rtn = await self.state.http.get_anything(
            Route("GET", "chat.getPermalink", self.state.http.user_token),
            data={
                "message_ts": message.id,
                "channel": self.id
            }
        )
        return rtn

    async def archive(self) -> None:
        """|coro|
        This channel archive as user.

        .. versionadded 1.3.0

        """
        param = {
            "channel": self.id
        }
        await self.state.http.create_channel(
            Route("POST", "conversations.archive", token=self.state.http.user_token),
            param
        )

    async def history(self) -> List[Message]:
        """
        Examples
        --------
        Examples ::

            async for message in channel.history():
                print(message.content)

        Returns
        -------

        """
        query = {
            "channel": self.id
        }
        msg = await self.state.http.get_anything(
            Route("GET", "conversations.history", self.state.http.bot_token),
            query=query
        )
        messages = msg["messages"]
        return [slack.Message(self.state, data=data) for data in messages]
