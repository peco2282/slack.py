from __future__ import annotations

from enum import Enum

__all__ = (
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
