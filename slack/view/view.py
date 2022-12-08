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

    Attributes
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
    This represents placeholder for :class:`Select` or :class:`Input`

    Attributes
    ----------
    text: :class:`str`
        Text for placeholder.

    mrkdwn: :class:`bool`
        Use markdown or not.

    emoji: :class:`bool`
        Use emoji or not.

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
        """Converts this object into a dict.
        Returns
        -------
        Dict[:class:`str`, Union[:class:`str`, :class:`bool`]]
            A dictionary of :class:`str` field keys bound to the respective value.
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
        """Converts this object into a dict.
        Returns
        -------
        Dict[:class:`str`, Union[:class:`str`, Dict[:class:`str`, Union[:class:`str`, :class:`bool`]]]
            A dictionary of :class:`str` field keys bound to the respective value.
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

    Attributes
    ----------
    blocks: List[:class:`BaseView`]
        Blocks of View.
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
        """Add block for self.

        Parameters
        ----------
        block: :class:`BaseView`

        Returns
        -------
        :class:`View`
        """
        if getattr(block, "__type__", "") == "__view__":
            self.blocks.append(block)

        return self

    def to_list(self):
        """Converts this object into a dict.

        Returns
        -------

        Dict[:class:`str`, Any]
            A dictionary of :class:`str` embed field keys bound to the respective value.

        """
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
