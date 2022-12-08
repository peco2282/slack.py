from __future__ import annotations

from typing import Union, TYPE_CHECKING
from .view import BaseView

if TYPE_CHECKING:
    from .view import Title, Label

__all__ = (
    "Image",
)


class Image(BaseView):
    def __init__(
            self,
            image_url: str,
            alt_text: str,
            title: Union[Title, Label] = None
    ):
        self.image_url = str(image_url)
        self.alt_text = str(alt_text)
        self.title = title

    def to_dict(self):
        param = {
            "type": "image",
            "image_url": self.image_url,
            "alt_text": self.alt_text
        }
        if self.title and isinstance(
                self.title,
                (Label, Title)
        ):
            param["title"] = self.title.to_dict()

        return param
