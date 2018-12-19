import sqlite3
from ..config import Config


class Database(object):

    def __init__(self, config: Config, filename: str = "database.db"):
        self.conn = sqlite3.connect(config.projectpath + filename)
        self.__config = config

    def __del__(self):
        self.conn.close()

    def create(self, filename: str):
        fd = open(filename, 'r')
        sql = fd.read()
        fd.close()

        c = self.conn.cursor()
        for command in sql.split(';'):
            try:
                c.execute(command)
            except Exception as e:
                print("Command skipped: %s" % str(e))
        self.conn.commit()
