import os
import json


class ConfigData(object):

    def __init__(self):
        """
        Config Data
        """
        self.bot_token = ""
        self.bot_prefix = "$"
        self.music_folder = ""

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


class Config(object):

    def __init__(self, project: str = "JakubiWeeb", filename: str = "config.json"):
        self.project = project
        self.__configpath = self.__get_project_name() + filename
        self.config = ConfigData()
        self.load()

    def __get_project_name(self):
        p = os.path.abspath(__file__).split(os.path.sep)
        if os.name == "nt":
            p[0] += os.path.sep
        return os.path.join(*p[:p.index(self.project) + 1]) + os.path.sep

    def load(self):
        try:
            fd = open(self.__configpath, 'r+')
            self.config = ConfigData.from_dict(json.loads(fd.read()))
            fd.close()
        except FileNotFoundError:
            print("Config file not found! Creating first config.")
            self.config = ConfigData()
            self.save()
        except KeyError:
            print("Invalid config file! Creating a new config.")
            self.config = ConfigData()
            self.save()

    def save(self):
        data = json.dumps(self.config.to_dict(), ensure_ascii=False)
        fd = open(self.__configpath, 'w+')
        fd.write(data)
        fd.close()
