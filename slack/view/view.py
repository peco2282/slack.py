from __future__ import annotations

__all__ = (
    "BaseView",
    "ViewFrame",
    "View",
    "InputSelect",
    "Button",
    "Placeholder",
    "Label",
    "Title"
)

from typing import TypeVar, TYPE_CHECKING

from ..errors import InvalidParamException

ViewT = TypeVar("ViewT")
if TYPE_CHECKING:
    pass


class BaseView:
    def __init_subclass__(cls, *args, **kwargs):
        setattr(cls, "__type__", "__view__")

    def to_dict(self):
        raise NotImplementedError()


class ViewFrame:
    def __init_subclass__(cls, *args, **kwargs):
        setattr(cls, "__type__", "__frame__")

    def to_list(self):
        raise NotImplementedError()


class Label(BaseView):
    """

    Parameters
    ----------
    text: :class:`str`
    mrkdwn: :class:`str`
    emoji: :class:`bool`

    """

    def __init__(
            self,
            text: str,
            mrkdwn: bool = True,
            emoji: bool = True
    ):
        self.text = str(text)
        self.mrkdwn = "mrkdwn" if mrkdwn else "plain_text"
        self.emoji = emoji if isinstance(emoji, bool) else True

    def to_dict(self):
        """

        Returns
        -------

        """
        return {
            "type": self.mrkdwn,
            "text": self.text,
            "emoji": self.emoji
        }


Title = Label


class InputSelect(BaseView):
    def __init__(
            self,
            *blocks
    ):
        pass

    def to_dict(self):
        pass


class Placeholder(BaseView):
    """
    Parameters
    ----------
    text
    mrkdwn
    emoji

    """

    def __init__(
            self,
            text: str,
            mrkdwn: bool = False,
            emoji: bool = False
    ):
        self.text = str(text)
        self.mrkdwn = "mrkdwn" if mrkdwn else "plain_text"
        self.emoji = emoji if isinstance(emoji, bool) else True

    def to_dict(self):
        """

        Returns
        -------

        """
        return {
            "type": self.mrkdwn,
            "text": self.text,
            "emoji": self.emoji
        }


class Button:
    """

    Parameters
    ----------
    label
    value
    action_id
    url
    """

    def __init__(
            self,
            label: Label,
            value: str,
            action_id: str,
            url: str = None
    ):
        if not isinstance(label, Label):
            raise InvalidParamException()
        self.label = label
        self.value = str(value)
        self.action_id = str(action_id)
        self.url = url

    def to_dict(self):
        """

        Returns
        -------

        """
        param = {
            "type": "button",
            "text": self.label.to_dict(),
            "value": self.value,
            "action_id": self.action_id
        }
        if self.url:
            param["url"] = str(self.url)

        return param


class View(ViewFrame):
    """

    Parameters
    ----------
    blocks
    """

    def __init__(
            self,
            *blocks: BaseView
    ):
        self.blocks = [
            b
            for b
            in blocks
            if isinstance(b, BaseView)
        ]

    def __len__(self):
        return len(self.blocks)

    def add_block(self, block: BaseView) -> View:
        if getattr(block, "__type__", "") == "__view__":
            self.blocks.append(block)

        return self

    def to_list(self):
        return [
            {
                "type": "actions",
                "elements": [
                    b.to_dict()
                    for b
                    in self.blocks
                ]
            }

        ]
