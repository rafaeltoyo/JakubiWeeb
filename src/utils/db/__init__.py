import sqlite3
from ..config import Config


class Database(object):

    def __init__(self, config: Config, filename: str = "database.db"):
        """
        Database access base class. Create and manage the connection with SQLite3 database.
        :param config:
        :param filename:
        """
        # Configuration
        self.__config = config
        self.__filename = self.__config.projectpath + filename

        try:
            self.conn = sqlite3.connect(self.__filename)  # type: sqlite3.Connection
        except Exception as e:
            print("Error in database connection: " + str(e))
            self.conn = None

    def __del__(self):
        """
        Interrupt and close the database connection.
        :return:
        """
        self.conn.interrupt()
        self.conn.close()

    def __enable_spellfix(self):
        """
        Enable spellfix plugin in SQLite3.
        https://stackoverflow.com/questions/49779281/string-similarity-with-python-sqlite-levenshtein-distance-edit-distance
        """
        self.conn.enable_load_extension(True)
        self.conn.load_extension(self.__config.projectpath.replace('\\', '/') + "spellfix.dll")
        self.conn.enable_load_extension(False)

    def exec(self, filename: str):
        """
        Read and execute a '.sql' file.
        :param filename: SQL file.
        """
        # Read file
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
