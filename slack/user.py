from .types import (
    User as UserPayload,
    Profile as ProfilePayload
)

__all__ = (
    "Profile",
    "User"
)


class Profile:
    def __init__(self, user: "User", data: ProfilePayload):
        """This function takes in a user and a data object and sets the user and data attributes of the Profile class to the
        user and data objects passed in

        Parameters
        ----------
        user : "User"
            The user object that is being updated.
        data : ProfilePayload
            The data that was sent to the API.

        """
        self.user = user
        self.data = data


# It creates a class called User.
class User:
    def __init__(self, data: UserPayload):
        """This function takes in a UserPayload object and assigns it to the data attribute of the User class

        Parameters
        ----------
        data : UserPayload
            The data to be sent to the API.

        """
        self.data = data
