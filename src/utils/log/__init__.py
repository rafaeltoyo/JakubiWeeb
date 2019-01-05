import datetime
import os

from ..config import Config
from ..singleton import Singleton


class Log(metaclass=Singleton):

    def __init__(self):
        self.__config = None
        self.__debug = False

    def set_config(self, config: Config):
        self.__config = config

    def set_debug(self):
        self.__debug = True

    def __generate_name(self, type=""):
        return self.__config.projectpath + "log" + os.path.sep + datetime.date.today().strftime(
            "%Y%m%d") + type + ".log"

    def __check(self):
        if self.__config is None:
            raise RuntimeError("Config not found!")

    def __create_log(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w+') as file:
            file.write("Log created at " + datetime.datetime.now().__str__() + '\n')

    def __write(self, txt: str, type="", lnbreak=True):
        if self.__debug:
            print(txt)
            return

        self.__check()
        filename = self.__generate_name(type=type)

        if not os.path.isfile(filename):
            self.__create_log(filename)

        with open(filename, 'a') as file:
            file.write(datetime.datetime.now().time().__str__() + ": " + txt + ('\n' if lnbreak else ''))

    def err(self, txt: str):
        self.__write(txt, type="error", lnbreak=True)

    def write(self, txt: str):
        self.__write(txt, type="info", lnbreak=True)
