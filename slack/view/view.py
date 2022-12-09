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
    """This class is base class for all components.

    This class carries abstract methods for all components.

    .. versionadded:: 1.4.0

    """

    def __init_subclass__(cls, *args, **kwargs):
        setattr(cls, "__type__", "__frame__")

    def to_list(self):
        raise NotImplementedError()


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

    .. versionadded:: 1.4.0

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


Label = Title = Placeholder


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
    """This is a frame of view block.

    .. versionadded:: 1.4.0

    .. container:: operations

        .. describe:: len(x)
            Returns the total length of the blocks.

        .. describe:: bool(b)
            Returns whether this has one or more blocks.

    Example:

    .. code-block:: python
        select = Select(
            "action",
            Placeholder(
                "text", mrkdwn=False, emoji=True),
                select_type=SelectType.users_select,
                initial_text="initial"
        )

        view = View(select)
        await message.channel.send(view=view)

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

    def __len__(self) -> int:
        return len(self.blocks)

    def __bool__(self) -> bool:
        return len(self.blocks) != 0

    def add_block(self, block: BaseView) -> View:
        """Add block to the view object.

        Parameters
        ----------
        block: :class:`BaseView`
            Add block to this view object.
            Block must be inherit :class:`BaseView`.

        Returns
        -------
        :class:`View`
            Returns self object.
        """
        if isinstance(block, BaseView):
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
