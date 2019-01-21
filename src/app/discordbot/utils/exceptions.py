from discord import Embed
from utils.log.manager import LogManager


class CustomError(Exception):

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg

    def to_embed(self):
        LogManager().err.println(self.msg)
        return Embed(

        )

class ErrorHandler:

    def __init__(self, log: bool = False):
        self.log = log

    def parse(self, e: Exception):
        if self.log is not None:
            LogManager().err.println(e)
