BASE = "https://slack.com/api/"


class Route:
    def __init__(self, method: str, endpoint: str, token: str):
        """This function takes in a method, endpoint, and token and sets them as attributes of the class

        Parameters
        ----------
        method : str
            The HTTP method to use.
        endpoint : str
            The endpoint you want to hit.
        token : str
            The token you got from the previous step.

        """
        self.method: str = method
        self.url: str = BASE + endpoint
        self.token: str = token

    @property
    def base(self) -> str:
        return BASE
