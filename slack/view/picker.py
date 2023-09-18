from __future__ import annotations

import datetime
import re

from .view import BaseView, Confirm, Text, ElementType
from ..errors import InvalidArgumentException


class DatePicker(BaseView):
    """An element which lets users easily select a date from a calendar style UI.
    To use interactive components like this, you will need to make some changes to prepare your app.
    Read our guide to enabling interactivity.

    Parameters
    ----------
    action_id: :class:`str`
        An identifier for the action triggered when a menu option is selected.
        You can use this when you receive an interaction payload to identify the source of the action.
        Should be unique among all other action_ids in the containing block.
        Maximum length for this field is 255 characters.

    initial_data: :class:`str`
        The initial date that is selected when the element is loaded.
        This should be in the format YYYY-MM-DD.

    confirm: :class:`Confirm`
        A confirm object that defines an optional confirmation dialog that appears after a date is selected.

    focus_on_load: :class:`bool`
        Indicates whether the element will be set to auto focus within the view object.
        Only one element can be set to true. Defaults to false.

    placeholder: :class:`Text`
        A plain_text only text object that defines the placeholder text shown on the datepicker.
        Maximum length for the text in this field is 150 characters.
    """

    def __init__(
            self,
            action_id: str,
            initial_data: str,
            confirm: Confirm | None = None,
            focus_on_load: bool = False,
            placeholder: Text | None = None
    ):
        self.action_id = action_id
        if len(re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", initial_data).groups()) == 0:
            raise InvalidArgumentException()

        self.initial_data = initial_data
        self.confirm = confirm
        self.focus_on_load = focus_on_load
        self.placeholder = placeholder

    def to_dict(self):
        payload = {
            "type": ElementType.DatePicker.value(),
            "action_id": self.action_id
        }
        if self.initial_data:
            payload["initial_date"] = self.initial_data

        if self.confirm:
            payload["confirm"] = self.confirm.to_dict()

        if self.focus_on_load:
            payload["focus_on_load"] = self.focus_on_load

        if self.placeholder:
            payload["placeholder"] = self.placeholder.to_dict()

        return payload


class DatetimePicker(BaseView):
    def __init__(
            self,
            action_id: str,
            initial_date_time: datetime.datetime | int | None = None,
            confirm: Confirm = None,
            focus_on_load: bool = False
    ):
        self.action_id = action_id
        self.initial_date_time: int = initial_date_time.timestamp() \
            if isinstance(initial_date_time, datetime.datetime) \
            else initial_date_time

        self.confirm = confirm
        self.focus_on_load = focus_on_load

    def to_dict(self):
        payload = {
            "type": ElementType.DatetimePicker.value(),
            "action_id": self.action_id
        }
        if self.initial_date_time:
            payload["initial_date_time"] = int(self.initial_date_time)

        if self.confirm:
            payload["confirm"] = self.confirm.to_dict()

        if self.focus_on_load:
            payload["focus_on_load"] = self.focus_on_load

        return payload
