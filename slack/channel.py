from __future__ import annotations

import json
import urllib.parse
from datetime import datetime
from typing import TYPE_CHECKING, Optional, overload, Union, List, Dict

from .errors import InvalidArgumentException
from .member import Member
from .message import Message
from .route import Route
from .team import Team
from .types.channel import (
    Channel as ChannelPayload,
    DeletedChannel as DeletedChannelPayload
)
from .utils import ts2time
from .view import ViewFrame
import slack

if TYPE_CHECKING:
    from .attachment import Attachment
    from .state import ConnectionState

__all__ = (
    "Channel",
    "DeletedChannel"
)


# > A `Channel` is a named pipe that can be used to send and receive messages
class Channel:
    """This function is a constructor for the Channel class. It takes in a ConnectionState object and a ChannelPayload
    object. It sets the state, id, name, team, created_at, and created_by attributes of the Channel object. It then
    calls the overload function

    Attributes
    ----------
    id : :class:`str`
        Channel ID.

    team : :class:`Team`
        Your team object.

    name: :class:`str`
        Account name.

    created_at: :class:`datetime`
        When create this channel.

    created_by: :class:`Member`
        Who channel create.

    """

    def __init__(self, state: ConnectionState, data: ChannelPayload):
        self.state = state
        self.id: str = data.get("id")
        self.name = data.get("name")
        self.team: Team = self.state.teams.get(data.get("context_team_id"), "")
        self.created_at: datetime = datetime.fromtimestamp(float(data.get("created", 0)))
        self.created_by: Optional[Member] = self.state.members.get(data.get("creator"))
        self.__http = self.state.http
        # self.overload(data)

    def __eq__(self, other) -> bool:
        if isinstance(other, Channel):
            return self.id == other.id

        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

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
            text: str
    ):
        ...

    @overload
    async def send(
            self,
            view: ViewFrame
    ):
        ...

    async def send(
            self,
            text: str = None,
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
        param = query = None
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

        message = await self.state.http.send_message(
            Route("POST", "chat.postMessage", token=self.state.http.bot_token),
            data=param,
            query=query
        )
        msg = Message(state=self.state, data=message["message"])
        msg.channel_id = self.id
        return msg

    async def send_as_user(self, text: str):
        """|coro|
        Message is sended by you. not application.

        .. deprecated:: 1.4.2
            Use :send: func.

        Parameters
        ----------
        text: :class:`str`
            Message you want to send by your.

        Returns
        -------
        :class:`Message`
            A Message object.

        """
        param = {
            "channel": self.id,
            "text": text
        }
        message = await self.state.http.send_message(
            Route(method="POST", endpoint="chat.postMessage", token=self.state.http.user_token),
            data=param
        )
        return Message(state=self.state, data=message["message"])

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
        if not any(
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

    async def unarchive(self):
        param = {
            "channel": self.id
        }
        rtn = await self.state.http.request(
            Route("POST", "channels.unarchive", self.state.http.bot_token),
            data=param
        )
        return rtn

    async def replies(self):
        rtn = await self.state.http.send_message(
            Route("GET", "conversations.replies", self.state.http.bot_token)
        )
        return rtn

    async def edit(
            self,
            title: str = None,
            purpose: str = None,
    ):
        pass


class DeletedChannel:
    """This function is called when a channel is deleted

    Attributes
    ----------
    channel_id : :class:`str`
        deleted channel id.

    """

    def __init__(self, state: ConnectionState, data: DeletedChannelPayload):
        self.state = state
        self.channel_id: str = data.get("channel")
        self.deleted_at: datetime = datetime.fromtimestamp(float(data.get("event_ts", "nan")))
