import abc
from .database import Database


class BaseDAO(metaclass=abc.ABCMeta):

    def __init__(self, table: str, fields: list, database: Database):
        self.__table = table
        self.__fields = [str(i) for i in fields]
        self.__db = database

    def __get_insert(self, *args):
        """
        Create insert statement
        :param args:
        :return:
        """

        sql = """INSERT INTO {} VALUES"""
