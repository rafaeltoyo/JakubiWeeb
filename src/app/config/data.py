class ConfigData(object):

    def __init__(self):
        """
        Config Data
        """
        self.bot_token = ""
        self.bot_prefix = "$"
        self.music_folder = ""

    def __str__(self):
        return str(self.to_dict())

    @staticmethod
    def from_dict(data: dict):
        """
        Load Config Data from dict
        :param data: Dict with data
        :type data: dict
        """
        c = ConfigData()
        c.bot_token = data["botToken"]
        c.bot_prefix = data["botPrefix"]
        c.music_folder = data["musicFolder"]
        return c

    def to_dict(self):
        """
        Convert Config Data to dict
        """
        return {
            "botToken": self.bot_token,
            "botPrefix": self.bot_prefix,
            "musicFolder": self.music_folder
        }
