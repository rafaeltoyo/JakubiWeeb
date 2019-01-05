class LMInvalidExtensionException(Exception):
    """
    LocalMusic: Invalid music file extension.
        See 'localmusic/loader.py' to find valid extensions
    """
    pass


class LMCreateConnectionException(Exception):
    """
    LocalMusic: Exception while creating sqlite3 connection.
        Origin 'localmusic/storage.py'
    """
    def __str__(self):
        return "Database connection exception: " + super().__str__()


class LMInvalidSearchParameter(Exception):
    """
    LocalMusic: Invalid search parameter type
    """
    def __str__(self):
        return "Search parameter must be string (match) or int (music id)"
