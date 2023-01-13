import datetime
from enum import Enum
from typing import Optional

from .select import SelectOption
from .view import BaseView, Placeholder
from ..errors import InvalidArgumentException


__all__ = (
    "Input",
    "InputType"
)


class InputType(Enum):
    plain_text_input = "plain_text_input",
    multi_users_select = "multi_users_select"
    static_select = "static_select"
    multi_static_select = "multi_static_select"
    datepicker = "datepicker"
    checkboxes = "checkboxes"
    radio_buttons = "radio_buttons"
    timepicker = "timepicker"

    def __str__(self):
        return self.name


class Input(BaseView):
    def __init__(
            self,
            action_id: str,
            dispatch_action: bool = False,
            multiline: bool = False,
            placeholder: Optional[Placeholder] = None,
            *select_options: SelectOption,
            label: Optional[Placeholder] = None,
            input_type: InputType = InputType.plain_text_input,
            initial_text: Optional[str] = None
    ):
        self.label = label if isinstance(label, Placeholder) else None
        self.dispatch_action = dispatch_action
        self.action_id = str(action_id)
        self.multiline = multiline
        self.placeholder = placeholder
        self.input_type: InputType = input_type \
            if isinstance(input_type, InputType) \
            else InputType.plain_text_input
        self.emoji = placeholder.emoji if placeholder else True
        self.initial_text = initial_text
        self.select_options = [
            s
            for s
            in select_options
            if isinstance(s, SelectOption)
        ]

    def to_dict(self):
        elem = {
            "type": self.input_type.name,
            "action_id": self.action_id
        }

        if self.input_type in (
                InputType.multi_users_select,
        ):
            placeholder = self.placeholder
            if not placeholder:
                placeholder = Placeholder(
                    text="Select a date",
                    mrkdwn=True,
                    emoji=True
                )
            elem["placeholder"] = placeholder.to_dict()

        if self.input_type == InputType.datepicker:
            initial_date = self.initial_text
            placeholder = self.placeholder
            if not initial_date:
                _date = datetime.datetime.now()
                initial_date = _date.strftime("%Y-%m-%d")

            if not placeholder:
                placeholder = Placeholder(
                    text="Select a date",
                    mrkdwn=True,
                    emoji=True
                )

            elem["initial_date"] = initial_date
            elem["placeholder"] = placeholder.to_dict()

        if self.input_type == InputType.timepicker:
            initial_time = self.initial_text
            placeholder = self.placeholder

            if not initial_time:
                initial_time = datetime.datetime.now().strftime("%h:%m")

            if not placeholder:
                placeholder = Placeholder(
                    text="Select time",
                    mrkdwn=True,
                    emoji=True
                )

            elem["initial_time"] = initial_time
            elem["placeholder"] = placeholder.to_dict()

        if self.input_type in (
                InputType.checkboxes,
                InputType.radio_buttons,
                InputType.static_select,
                InputType.multi_static_select,
        ):
            if len(self.select_options) <= 1:
                raise InvalidArgumentException("options must be 2 or more.")

            elem["options"] = [
                s.to_dict()
                for s
                in self.select_options
            ]

        block = {
            # "dispatch_action": self.dispatch_action,
            "type": "input",
            "element": elem
        }
        if not self.label:
            self.label = Placeholder(text="Label", mrkdwn=True, emoji=True)
        block["label"] = self.label.to_dict()

        return block
