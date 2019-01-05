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
        """
        Create a configuration controller
        :param project: Project name. Default: JakubiWeeb (from github)
        :param filename: Configuration file name.
        """
        # Project name (folder name).
        self.project = project

        self.projectpath = self.__get_project_path()
        self.__configpath = self.projectpath + filename

        # Entity with Config Data. Converts JSON file to Python class.
        self.config = ConfigData()

        self.load()

    def __get_project_path(self):
        """
        Get absolute path of project
        :return: Absolute path of project
        """

        p = os.path.abspath(__file__).split(os.path.sep)
        if os.name == "nt":  # Windows
            p[0] += os.path.sep
        return os.path.join(*p[:p.index(self.project) + 1]) + os.path.sep

    def load(self):
        """
        Load config file
        :return:
        """
        try:
            fd = open(self.__configpath, 'r+')
            # File -> Memory
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
        except Exception as e:
            raise e

    def save(self):
        """
        Save config file
        :return:
        """
        data = json.dumps(self.config.to_dict(), ensure_ascii=False)
        fd = open(self.__configpath, 'w+')
        # Memory -> File
        fd.write(data)
        fd.close()
