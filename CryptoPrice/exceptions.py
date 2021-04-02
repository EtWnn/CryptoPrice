class RateAPIException(Exception):
    """
    An exception to be raised when an API was requested beyond the limits
    """

    def __init__(self, retry_after: float, *args):
        self.retry_after = retry_after
        super().__init__(*args)

