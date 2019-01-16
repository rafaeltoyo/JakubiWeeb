
import datetime
import os
import enum
from pathlib import Path

from ..filesystem import PathBuilder
from ..singleton import Singleton


class Buffer:

    def __init__(self, filename=None, prefix: str = None, console: bool = False):
        self.__buffer = Path(str(filename)) if filename is not None else None
        self.__prefix = prefix
        self.__console = console

    def __get_prefix(self) -> str:
        return "{} {}: ".format(self.__prefix, datetime.datetime.now())

    def print(self, m):
        if self.__prefix is not None:
            m = self.__get_prefix() + m
        if self.__buffer is not None:
            with self.__buffer.open('w+') as f:
                f.write(m)
            if self.__console:
                print(m)
        else:
            print(m)

    def println(self, m):
        self.print(str(m) + os.linesep)


class LogManager(metaclass=Singleton):

    def __init__(self):
        self.__err_buffer = Buffer(filename=None, prefix="ERROR")
        self.__out_buffer = Buffer(filename=None, prefix="INFO")
        self.__debug_buffer = Buffer(filename=None, prefix="DEBUG")

    def redefine_default_files(self):
        self.redefine(
            out_file=str(PathBuilder().log / (datetime.date.today().strftime("%Y%m%d") + "INFO.log")),
            err_file=str(PathBuilder().log / (datetime.date.today().strftime("%Y%m%d") + "ERROR.log")),
            debug_file=str(PathBuilder().log / (datetime.date.today().strftime("%Y%m%d") + "DEBUG.log"))
        )

    def redefine(self, out_file=None, err_file=None, debug_file=None):
        self.__err_buffer = Buffer(filename=err_file, prefix="ERROR")
        self.__out_buffer = Buffer(filename=out_file, prefix="INFO")
        self.__debug_buffer = Buffer(filename=debug_file, prefix="DEBUG")

    @property
    def err(self):
        return self.__err_buffer

    @property
    def out(self):
        return self.__out_buffer

    @property
    def debug(self):
        return self.__debug_buffer
