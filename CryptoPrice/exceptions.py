import requests


class RateAPIException(Exception):
    """
    An exception to be raised when an API was requested beyond the limits
    """

    def __init__(self, response: requests.Response, retry_after: float):
        self.retry_after = retry_after
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

