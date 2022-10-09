from .types import (
    Icon as IconPayload,
    Team as TeamPayload
)

__all__ = (
    "Icon",
    "Team"
)


class Icon:
    def __init__(self, team: "Team", data: IconPayload):
        """This function is used to initialize the Icon class

        Parameters
        ----------
        team : "Team"
            The team that the icon is for.
        data : IconPayload
            The data that was sent to the webhook.

        """
        self.data = data
        self.team = team


class Team:
    def __init__(self, state, data: TeamPayload):
        """This function takes in a TeamPayload object and sets the data attribute of the Team object to the TeamPayload object

        Parameters
        ----------
        data : TeamPayload
            The data that was sent to the webhook.

        """
        self.data = data
