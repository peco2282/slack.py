from .view import ViewFrame, Button


class Modal(ViewFrame):
    def __init__(
            self,
            title: str,
            submit_label: str,
            cancel_label: str,
            *blocks: Button
    ):
        self.title = str(title)
        self.submit_label = str(submit_label)
        self.cancel_label = str(cancel_label)
        self.blocks = [
            b.to_dict()
            for b
            in blocks
            if isinstance(b, Button)
        ]

    def to_list(self):
        title = {
            "type": "plain_text",
            "text": self.title,
            "emoji": True
        }
        submit = {
            "type": "plain_text",
            "text": self.submit_label,
            "emoji": True
        }
        close = {
            "type": "plain_text",
            "text": self.cancel_label,
            "emoji": True
        }
        param = {
            "type": "modal",
            "title": title,
            "submit": submit,
            "close": close,
            "blocks": self.blocks
        }
        return param
