from .select import Select
from .view import BaseView


class Action(BaseView):
    def __init__(
            self,
            *elements: Select
    ):
        self.elements = elements

    def to_dict(self):
        elements = [
            o.to_dict()
            for o
            in self.elements
            if isinstance(o, Select)
        ]
        return {
            "type": "actions",
            "elements": elements
        }
