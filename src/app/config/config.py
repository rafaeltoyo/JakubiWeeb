import json

from .data import ConfigData
from utils.filesystem import *


class Config(object):

    def __init__(self, cf: str = None):
        """
        Create a configuration controller
        :param cf: Configuration filename.
        """
        # Create absolute path from user defined config filename or just get default config filename
        self.__configpath = (PathBuilder().project / cf) if cf is not None else PathBuilder().config_file

        # Entity with Config Data. Converts JSON file to Python class.
        self.params = ConfigData()

    def load(self):
        """
        Load config file.
        If the file already exists load the data
        else create a default config data and save.
        :return: Nothing
        """
        try:
            # Open config file and read the parameters
            with self.__configpath.open('r+') as fd:

                # Load JSON data as ConfigData
                self.params = ConfigData.from_dict(json.loads(fd.read()))

        except FileNotFoundError:
            print("Config file not found! Creating first config.")
            self.params = ConfigData()
            self.save()

        except KeyError:
            print("Invalid config file! Creating a new config.")
            self.params = ConfigData()
            self.save()

        except Exception as e:
            raise e

    def save(self):
        """
        Save config file
        :return: Nothing
        """
        # Get JSON string from dict generated from ConfigData
        data = json.dumps(self.params.to_dict(), ensure_ascii=False)

        # Open config file and write json string generated
        with self.__configpath.open('w+') as fd:
            fd.write(data)
