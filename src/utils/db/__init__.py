import sqlite3
from ..config import Config


class Database(object):

    def __init__(self, config: Config, filename: str = "database.db"):
        self.conn = sqlite3.connect(config.projectpath + filename)  # type: sqlite3.Connection
        # https://stackoverflow.com/questions/49779281/string-similarity-with-python-sqlite-levenshtein-distance-edit-distance
        # self.conn.enable_load_extension(True)
        # self.conn.load_extension("./spellfix.dll")
        # self.conn.enable_load_extension(False)
        self.__config = config

    def __del__(self):
        self.conn.interrupt()
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
