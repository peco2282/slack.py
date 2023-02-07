from __future__ import annotations

__all__ = (
    "BaseView",
    "ViewFrame",
    "View",
    "InputSelect",
    "Placeholder",
    "Label",
    "Title",
    "ActionView",
    "SectionView"
)

from typing import TypeVar, TYPE_CHECKING

ViewT = TypeVar("ViewT")
if TYPE_CHECKING:
    pass


class BaseView:
    """Base class of view object.

    This class carries abstract methods for all components.

    .. versionadded:: 1.4.0
    """

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


class View(ViewFrame):
    """This is a frame of view block.
    All blocks contains this instance.

    .. versionadded:: 1.4.0

    .. container:: operations

        .. describe:: len(x)

            Returns the total length of the blocks.

        .. describe:: bool(b)

            Returns whether this has one or more blocks.

    Example: ::

        select = Select(
            action_id="action",
            placeholder=Placeholder(
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
            *blocks: ActionView | SectionView
    ):
        self.blocks = [
            b
            for b
            in blocks
            if isinstance(b, (ActionView, SectionView))
        ]

    def __len__(self) -> int:
        return len(self.blocks)

    def __bool__(self) -> bool:
        return len(self.blocks) != 0

    def add_block(self, block: ActionView | SectionView) -> View:
        """Add block to the view object.

        Parameters
        ----------
        block: Union[:class:`ActionView`, :class:`SectionView`]
            Add block to this view object.
            Block must be inherit :class:`BaseView`.

        Returns
        -------
        :class:`View`
            Returns self object.
        """

        if isinstance(block, (ActionView, SectionView)):
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
            b.to_dict()
            for b
            in self.blocks
        ]


class SectionView(BaseView):
    """This class create `section` type instance.

    .. versionadded:: 1.4.2

    Attributes
    ----------
    block: :class:`BaseView`
        Component of block. MUst inherit :class:`BaseView`.

    text: :class:`str`
        Text of block.

    """
    def __init__(
            self,
            block: BaseView,
            text: str
    ):
        self.block = block
        self.text = text

    def to_dict(self):
        """`to_dict` is a function that takes in a `self` object and returns a list of dictionaries

        Returns
        -------
            A list of dictionaries.

        """
        text = {
            "type": "mrkdwn",
            "text": str(self.text)
        }
        return {
            "type": "section",
            "text": text,
            "accessory":
                self.block.to_dict()
                if isinstance(self.block, BaseView)
                else {}
        }


class ActionView(BaseView):
    """This class create `action` type instance.

    .. versionadded:: 1.4.2

    Attributes
    ----------
    blocks: :class:`BaseView`
        Component of blocks. MUst inherit :class:`BaseView`.
    """
    def __init__(self, *block: BaseView) -> None:
        self.blocks = block

    def to_dict(self):
        """
        It takes a list of blocks, and returns a dictionary with the key "elements"
        and the value of a list of dictionaries,
        where each dictionary is the result of calling the to_dict() method on each block

        Returns
        -------
            A dictionary with the key "type" and the value "actions"

        """
        return {
            "type": "actions",
            "elements": [
                e.to_dict()
                for e
                in self.blocks
                if isinstance(e, BaseView)
            ]
        }
