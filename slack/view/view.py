from __future__ import annotations

__all__ = (
    "BaseView",
    "ViewFrame",
    "ElementType",
    "Text",
    "Confirm",
    "Button",
    "Option",
    "CheckBox",
    "EmailInput",
    "Style"
)

from abc import abstractmethod
from enum import Enum
from typing import TypeVar, TYPE_CHECKING

from ..errors import InvalidArgumentException

ViewT = TypeVar("ViewT")
if TYPE_CHECKING:
    pass


class ElementType(Enum):
    Button = "button"
    CheckBoxes = "checkboxes"
    DatePicker = "datepicker"
    DatetimePicker = "datetimepocker"
    EmailTextInput = "email_text_input"
    Image = "image"
    MultiStaticSelect = "multi_static_select"
    MultiExternalSelect = "multi_external_select"
    MultiUsersSelect = "multi_users_select"
    MultiConversationsSelect = "multi_conversations_select"
    MultiChannelsSelect = "multi_channels_select"
    NumberInput = "number_input"
    OverFlow = "overflow"
    PlainTextInput = "plain_text_input"
    RadioButtons = "radio_buttons"
    StaticSelect = "static_select"
    ExternalSelect = "external_select"
    UsersSelect = "users_select"
    ConversationsSelect = "conversations_select"
    ChannelsSelect = "channels_select"
    TimePicker = "time_picker"
    UrlTextInput = "url_text_input"
    WorkflowButton = "workflow_button"

    def value(self) -> str:
        return self._value_.lower()


class Style(Enum):
    DEFAULT = ""
    PRIMARY = "primary"
    DANGER = "danger"

    def name(self) -> str:
        return self._name_.lower()


class BaseView:
    """Base class of view object.

    This class carries abstract methods for all components.

    .. versionadded:: 1.4.0
    """

    def __init_subclass__(cls, *args, **kwargs):
        setattr(cls, "__type__", "__view__")

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class ViewFrame:
    """This class is base class for all components.

    This class carries abstract methods for all components.

    .. versionadded:: 1.4.0

    """

    def __init_subclass__(cls, *args, **kwargs):
        setattr(cls, "__type__", "__frame__")

    def to_list(self):
        raise NotImplementedError()


# TODO IMPLEMENTATION


class Text(BaseView):
    """An object containing some text, formatted either as plain_text or using mrkdwn,
     our proprietary contribution to the much beloved Markdown standard.

    Parameters
    ----------
    text: :class:`str`
        The text for the block. This field accepts any of the standard text formatting markup when type is mrkdwn.
        The minimum length is 1 and maximum length is 3000 characters.

    mrkdown: :class:`bool`
        The text is markdown or not.

    emoji: :class:`bool`
        When set to false (as is default) URLs will be auto-converted into links,
        conversation names will be link-ified, and certain mentions will be automatically parsed.

        Using a value of true will skip any preprocessing of this nature,
        although you can still include manual parsing strings.
        This field is only usable when type is mrkdwn.

    verbatim: :class:`bool`
        Indicates whether emojis in a text field should be escaped into the colon emoji format.
        This field is only usable when type is plain_text.

    Examples
    ---------
    initial parameters ::

        from slack import view

        text = view.Text("New text", emoji=True)

    """

    def __init__(self, text: str, *, mrkdown: bool = True, emoji: bool = False, verbatim: bool = False):
        if len(text) > 3000 or len(text) < 1:
            raise InvalidArgumentException("The minimum length is 1 and maximum length is 3000 characters.")
        self.text = text
        self.mrkdown = mrkdown
        self.emoji = emoji if mrkdown is False else False
        self.verbatim = verbatim if mrkdown else False

    def to_dict(self):
        return {
            "type": "mrkdown" if self.mrkdown else "plain_text",
            "text": str(self.text),
            "emoji": self.emoji,
            "verbatim": self.verbatim
        }


class Confirm(BaseView):
    """An object that defines a dialog that provides a confirmation step to any interactive element.
    This dialog will ask the user to confirm their action by offering a confirm and deny buttons.

    Parameters
    ----------
    title: :class:`str`
        A plain_text-only text object that defines the dialog's title.
        Maximum length for this field is 100 characters.

    field_text: :class:`str`
        A plain text-only text object that defines the explanatory text that appears in the confirm dialog.
        Maximum length for the text in this field is 300 characters.

    confirm_text: :class:`str`
        A plain_text-only text object to define the text of the button that confirms the action.
        Maximum length for the text in this field is 30 characters.
    
    deny_text: :class:`str`
        A plain_text-only text object to define the text of the button that cancels the action.
        Maximum length for the text in this field is 30 characters.
    """

    def __init__(
            self,
            title: str,
            field_text: str,
            confirm_text: str,
            deny_text: str
    ):
        self.title = str(title)
        self.field_text = str(field_text)
        self.confirm_text = str(confirm_text)
        self.deny_text = str(deny_text)

    def to_dict(self):
        plain = "plain_text"
        return {
            "title": {
                "type": plain,
                "text": self.title
            },
            "text": {
                "type": plain,
                "text": self.field_text
            },
            "confirm": {
                "type": plain,
                "text": self.confirm_text
            },
            "deny": {
                "type": plain,
                "text": self.deny_text
            },
        }


class Option(BaseView):
    """
    An object that represents a single selectable item in a `select menu
    <element:select>`_, multi-select menu, checkbox group,
    radio button group, or overflow menu.

    Parameters
    ----------
    text: :class:`Text`
        A text object that defines the text shown in the option on the menu.
        Overflow, select, and multi-select menus can only use plain_text objects,
        while radio buttons and checkboxes can use mrkdwn text objects.
        Maximum length for the text in this field is 75 characters.

    value: :class:`str`
        A unique string value that will be passed to your app when this option is chosen.
        Maximum length for this field is 75 characters.

    description: :class:`str`
        A plain_text only text object that defines a line of descriptive text shown below the text field
        beside the radio button. Maximum length for the text object within this field is 75 characters.

    url: :class:`str`:
        A URL to load in the user's browser when the option is clicked.
        The url attribute is only available in overflow menus.
        Maximum length for this field is 3000 characters.
        If you're using url, you'll still receive
        an interaction payload and will need to send an acknowledgement response.
    """

    def __init__(
            self,
            text: Text,
            value: str,
            description: str | None = None,
            url: str | None = None
    ):
        self.text = text
        self.value = value
        self.description = description
        self.url = url

    def to_dict(self):
        return {
            "text": self.text.to_dict(),
            "value": self.value
        }


class Button(BaseView):
    """
    An interactive component that inserts a button.
    The button can be a trigger for anything from opening a simple link to starting a complex workflow.

    To use interactive components, you will need to make some changes to prepare your app.
    Read our :resource:`guide to enabling <handling>` interactivity.

    Parameters
    ----------
    text: :class:`Text`
        A :class:`Text` object that defines the button's text. Can only be of type: plain_text.
        text may truncate with ~30 characters. Maximum length for the text in this field is 75 characters.

    action_id: :class:`str`
        An identifier for this action.
        You can use this when you receive an interaction payload to
        :resource:`identify the source of the action <handling:payloads>`.
        Should be unique among all other action_ids in the containing block.
        Maximum length for this field is 255 characters.

    url: :class:`str`
        A URL to load in the user's browser when the button is clicked.
        Maximum length for this field is 3000 characters.
        If you're using url, you'll still receive an :resource:`interaction payload<handling:payloads>`
        and will need to send an :resource:`acknowledgement response<handling:acknowledgment_response>`.

    value: :class:`str`
        The value to send along with the interaction payload. Maximum length for this field is 2000 characters.

    style: :class:`Style`
        Decorates buttons with alternative visual color schemes. Use this option with restraint.
        primary gives buttons a green outline and text, ideal for affirmation or confirmation actions.
        primary should only be used for one button within a set.
        danger gives buttons a red outline and text, and should be used when the action is destructive.

        Use danger even more sparingly than primary.
        If you don't include this field, the default button style will be used.
        Three buttons showing default, primary, and danger color styles

    confirm: :class:`Confirm`
        A :class:`Confirm` object that defines an optional confirmation dialog after the button is clicked.

    accessibility_lavel: :class:`str`
        A label for longer descriptive text about a button element.
        This label will be read out by screen readers instead of the button :class:`Text` object.
        Maximum length for this field is 75 characters.
    """

    def __init__(
            self,
            text: Text,
            action_id,
            *,
            url: str | None = None,
            value: str | None = None,
            style: Style = Style.DEFAULT,
            confirm: Confirm | None = None,
            accessibility_lavel: str | None = None
    ):
        self.__type = ElementType.Button.value()
        self.text = text
        self.action_id = action_id
        self.mkdown = text.mrkdown
        self.emoji = text.emoji
        self.url = url
        self.value = value
        self.style = style
        self.confirm = confirm
        self.accessibility = accessibility_lavel

    def to_dict(self):
        payload = {
            "type": ElementType.Button.value(),
            "text": self.text.to_dict(),
            "action_id": self.action_id
        }
        if self.style is not Style.DEFAULT:
            payload["style"] = self.style.name()

        if self.value:
            payload["value"] = str(self.value)

        if self.accessibility:
            payload["accessibility_lavel"] = self.accessibility

        if self.url:
            payload["url"] = self.url

        if self.confirm:
            payload["confirm"] = self.confirm.to_dict()

        return payload


class CheckBox(BaseView):
    """A checkbox group that allows a user to choose multiple items from a list of possible options.
    Checkboxes are only supported in the following :resource:`app surfaces<slack:surfaces>`_ :
    `Home tabs` `Modals` `Messages`
    To use interactive components like this, you will need to make some changes to prepare your app.
    Read our :resource:`guide to enabling interactivity<handling>`.

    Parameters
    ----------
    action_id: :class:`str`
        An identifier for the action triggered when the checkbox group is changed.
        You can use this when you receive an interaction payload to :resource:`identify the source of the action.<handling:payload>`_
        Should be unique among all other action_ids in the containing block.
        Maximum length for this field is 255 characters.

    options: list[:class:`Option`]
        An array of option objects. A maximum of 10 options are allowed.

    initial_options: list[:class:`Option`]
        An array of option objects that exactly matches one or more of the options within options.
        These options will be selected when the checkbox group initially loads.

    confirm: :class:`Confirm`
        A confirm object that defines an optional confirmation dialog that appears
         after clicking one of the checkboxes in this element.

    focus_on_load: :class:`bool`
        Indicates whether the element will be set to auto focus within the view object.
        Only one element can be set to true. Defaults to false.
    """

    def __init__(
            self,
            action_id: str,
            options: list[Option],
            /,
            initial_options: list[Option] = None,
            confirm: Confirm | None = None,
            focus_on_load: bool = False
    ):
        self.action_id = action_id
        self.options = options
        self.initial_options = initial_options
        self.confirm = confirm
        self.focus_on_load = focus_on_load

    def to_dict(self):
        payload = {
            "type": ElementType.CheckBoxes.value(),
            "action_id": self.action_id,
            "options": [o.to_dict() for o in self.options]
        }
        if self.initial_options:
            payload["initial_options"] = [o.to_dict() for o in self.initial_options]

        if self.confirm:
            payload["confirm"] = self.confirm.to_dict()

        if self.focus_on_load:
            payload["focus_on_load"] = self.focus_on_load

        return payload


class EmailInput(BaseView):
    def __init__(
            self,
            action_id: str,
            initial_value: str,
            dispatch_action_config: list[str],
            focus_on_load: bool,
            placeholder: Text
    ):
        self.action_id = action_id
        self.initial_value = initial_value
        self.dispatch_action_config = dispatch_action_config
        self.focus_on_load = focus_on_load
        self.placeholder = placeholder

    def to_dict(self):
        payload = {
            "type": ElementType.EmailTextInput.value(),
            "action_id": self.action_id
        }
        if self.placeholder:
            payload["placeholder"] = self.placeholder.to_dict()

        if self.focus_on_load:
            payload["focus_on_load"] = self.focus_on_load

        if len(self.dispatch_action_config) != 0:
            payload["dispatch_action_config"] = self.dispatch_action_config

        return payload
