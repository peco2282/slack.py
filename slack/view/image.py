from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .view import BaseView

if TYPE_CHECKING:
    from .view import Placeholder

__all__ = (
    "Image",
)


class Image(BaseView):
    """This is the class used to mount images on the ui.

    .. versionadded:: 1.4.0

    Attributes
    ----------
    image_url: :class:`str`
        Url of image.

    alt_text: :class:`str`
        Description of this image.

    title: Optional[:class:`str`]
        Title of this image.

    """
    def __init__(
            self,
            image_url: str,
            alt_text: str,
            title: Optional[Placeholder] = None
    ):
        self.image_url = str(image_url)
        self.alt_text = str(alt_text)
        self.title = title

    def to_dict(self):
        """Converts this object into a dict.

        Returns
        -------
        Dict[:class:`str`, :class:`str`]
            A dictionary of :class:`str` field keys bound to the respective value.
        """
        param = {
            "type": "image",
            "image_url": self.image_url,
            "alt_text": self.alt_text
        }
        if self.title and isinstance(self.title, Placeholder):
            param["title"] = self.title.to_dict()

        return param
