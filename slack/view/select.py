from enum import Enum

from .view import BaseView, Placeholder
from ..errors import InvalidParamException

__all__ = (
    "SelectType",
    "SelectOption",
    "Select",
)


class SelectType(Enum):
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

    def __str__(self) -> str:
        return self.name


class SelectOption(BaseView):
    def __init__(
            self,
            text: str,
            value: str,
            description: str = None,
            mrkdwn: bool = True,
            emoji: bool = True
    ):
        self.text = str(text)
        self.value = str(value)
        self.mrkdwn = "mrkdwn" if mrkdwn else "plain_text"
        self.emoji = emoji
        self.description = description

    def to_dict(self):
        return {
            "text": {
                "type": self.mrkdwn,
                "text": self.text,
                "emoji": self.emoji
            },
            "description": {
                "type": self.mrkdwn,
                "text": self.text,
                "emoji": self.emoji
            },
            "value": self.value
        }


class Select(BaseView):
    def __init__(
            self,
            action_id: str,
            placeholder: Placeholder,
            *options: SelectOption,
            select_type: SelectType = SelectType.static_select,
            initial_text: str = None
    ):
        if not isinstance(placeholder, Placeholder):
            raise InvalidParamException()
        if options and not isinstance(select_type, SelectType):
            raise ValueError(f"select_type is only SelectType.")
        self.select_type = str(
            SelectType.static_select
            if not isinstance(
                select_type, SelectType
            )
            else select_type
        )
        if placeholder.mrkdwn is True:
            placeholder.mrkdwn = False
        self.placeholder = placeholder
        self.action_id = action_id
        self.options = options
        self.initial_text = str(initial_text)

    def to_dict(self):
        param = {
            "type": self.select_type,
            "placeholder": self.placeholder.to_dict(),
            "action_id": self.action_id
        }

        if self.select_type in (
                SelectType.static_select,
                SelectType.checkboxes,
                SelectType.radio_buttons
        ):
            if len(self.options) <= 1:
                raise InvalidParamException(
                    "options must 2 or more."
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
