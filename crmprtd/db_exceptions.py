class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class InsertionError(Error):
    """
    Exception raised for any errors inserting into database.

    Attributes:
        data -- the data that was attempted to be inserted
    """

    def __init__(self, **kwargs):
        self.data = kwargs

    def __str__(self):
        s = "Database Insertion Error using data: "
        for k, v in self.data.iteritems():
            s += "{0}: {1}, ".format(k, v)
        return s
