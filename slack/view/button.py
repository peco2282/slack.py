from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .view import BaseView

if TYPE_CHECKING:
    from ..errors import InvalidArgumentException
    from .view import Label


class Button(BaseView):
    """

    Attributes
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
            url: Optional[str] = None
    ):
        if not isinstance(label, Label):
            raise InvalidArgumentException()
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


class ButtonOption(BaseView):
    def __init__(
            self,
            text: str,
            description: Optional[str] = None,
            value: Optional[str] = None,
            mrkdwn: bool = True):
        self.text = str(text)
        self.desscription = str(description)
        self.value = str(value)
        self.mrkdwn = "mrkdwn" if mrkdwn else "plain_text"

    def to_dict(self):
        param = {
            "text": {
                "type": self.mrkdwn,
                "text": self.text
            }
        }
        if self.desscription:
            param["description"] = {
                "type": self.mrkdwn,
                "text": self.desscription
            }

        if self.value:
            param["value"] = self.value
        return param


class CheckBox(BaseView):
    def __init__(
            self,
            *block
    ):
        self.blocks = [b for b in block if isinstance(b, ButtonOption)]

    def to_dict(self):
        pass


class RadioButton(BaseView):
    def __init__(self):
        pass

    def to_dict(self):
        pass
