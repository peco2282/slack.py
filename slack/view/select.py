from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from .view import BaseView, Placeholder

if TYPE_CHECKING:
    # from .view import Placeholder
    from ..errors import InvalidArgumentException

__all__ = (
    "SelectType",
    "SelectOption",
    "Select",
)


class SelectType(Enum):
    """Enums of select variety.

    .. versionadded:: 1.4.0
    """
    conversations_select = "conversations_select"
    channels_select = "channels_select"
    users_select = "users_select"
    static_select = "static_select"
    plain_text_input = "plain_text_input",
    multi_users_select = "multi_users_select"
    multi_static_select = "multi_static_select"
    datepicker = "datepicker"
    checkboxes = "checkboxes"
    radio_buttons = "radio_buttons"
    timepicker = "timepicker"

    button = "button"
    link_button = "button"
    overflow = "overflow"
    image = "image"

    def __str__(self) -> str:
        return self.name


class SelectOption(BaseView):
    """Option for select items.

    .. versionadded:: 1.4.0

    Attributes
    ----------
    text: :class:`str`
        Text of select.

    value: :class:`str`
        Value of select.

    description: Optional[:class:`str`]
        Text description of select.

    mrkdwn: Optional[:class:`bool`]
        Markdown or nor.

    emoji: Optional[:class:`bool`]
        Use emoji or not
    """
    def __init__(
            self,
            text: str,
            value: str,
            description: str = None,
            mrkdwn: bool = True,
            # emoji: bool = True
    ):
        self.text = str(text)
        self.value = str(value)
        self.mrkdwn = "mrkdwn" if mrkdwn else "plain_text"
        # self.emoji = emoji
        self.description = description

    def to_dict(self):
        """Converts this object into a dict.

        .. versionadded:: 1.4.0

        Returns
        -------
        Dict[:class:`str`, Dict[:class:`str`, Union[:class:`str`, :class:`bool`]]]
            A dictionary of :class:`str` field keys bound to the respective value.
        """
        return {
            "text": {
                "type": self.mrkdwn,
                "text": self.text,
                # "emoji": self.emoji
            },
            "description": {
                "type": self.mrkdwn,
                "text": self.text,
                # "emoji": self.emoji
            },
            "value": self.value
        }


class Select(BaseView):
    """Represents a UI select menu with a list of custom options.

    .. versionadded:: 1.4.0

    Attributes
    ----------
    action_id: :class:`str`
        ID for this event occured.

    placeholder: :class:`Placeholder`
        Placeholder of select.

    options: List[:class:`SelectOption`]
        Options to selections.
        Some type must be this attribute to select.

    select_type: :class:`SelectType`
        Select type of this object.

    initial_text: :class:`str`
        Initial text for selections.
    """
    def __init__(
            self,
            action_id: str,
            /,
            *options: SelectOption,
            placeholder: Placeholder = None,
            select_type: SelectType = SelectType.static_select,
            initial_text: str = None
    ):
        if placeholder is not None and not isinstance(placeholder, Placeholder):
            raise InvalidArgumentException()
        if options is not None and not isinstance(select_type, SelectType):
            raise ValueError(f"select_type is only SelectType.")
        self.select_type = select_type if isinstance(select_type, SelectType) else SelectType.static_select

        if placeholder is not None and placeholder.mrkdwn is True:
            placeholder.mrkdwn = False
        self.placeholder = placeholder
        self.action_id = action_id
        self.options = options
        self.initial_text = str(initial_text)

    def to_dict(self):
        """Converts this object into a dict.

        Returns
        -------
        Dict[:class:`str`, Any]
            A dictionary of :class:`str` field keys bound to the respective value.
        """
        param = {
            "type": str(self.select_type),
            # "placeholder": self.placeholder.to_dict(),
            "action_id": self.action_id
        }

        if self.select_type not in (
            SelectType.radio_buttons,
            SelectType.checkboxes,
            SelectType.button,
            SelectType.image
        ):
            if self.placeholder is None:
                raise InvalidArgumentException(f"`placeholder` must be required {self.select_type}.")

            param["placeholder"] = self.placeholder.to_dict()

        if self.select_type in (
                SelectType.static_select,
                SelectType.checkboxes,
                SelectType.radio_buttons
        ):
            if len(self.options) <= 1:
                raise InvalidArgumentException(
                    f"options must 2 or more. but you put {len(self.options)}."
                )
            param["options"] = [
                o.to_dict()
                for o
                in self.options
                if isinstance(o, SelectOption)
            ]

        if self.select_type == SelectType.conversations_select:
            if not self.initial_text:
                self.initial_text = "G12345678"
            param["initial_conversation"] = self.initial_text

        return param
