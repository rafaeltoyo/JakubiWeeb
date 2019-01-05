import sqlite3

from ..filesystem import *


class Database:
    # FIXME: Every execution method in this class should accept the same cursor instead of always creating another.

    conn: sqlite3.Connection

    def __init__(self, filename):
        """
        Database access base class. Create and manage the connection with SQLite3 database.
        :param filename: SQLite3 storage file
        """

        try:
            self.conn = sqlite3.connect(str(filename))
        except Exception as e:
            self.conn = None
            raise e

    def __del__(self):
        """
        Interrupt and close the database connection.
        :return:
        """
        if self.conn is not None:
            self.conn.interrupt()
            self.conn.close()

    def __enable_spellfix(self):
        """
        Enable spellfix plugin in SQLite3.
        https://stackoverflow.com/questions/49779281/string-similarity-with-python-sqlite-levenshtein-distance-edit-distance
        """
        self.conn.enable_load_extension(True)
        self.conn.load_extension(str(PathBuilder().project / "spellfix.dll"))
        self.conn.enable_load_extension(False)

    def exec_sql(self, statement, args=None):
        with self.conn:
            c = self.conn.cursor()

            try:
                if args == None:
                    c.execute(statement)
                else:
                    c.execute(statement, args)
                self.conn.commit()
                return c

            except Exception as e:
                self.conn.rollback()
                c.close()
                raise e

    def exec_insert(self, statement, args):
        with self.conn:
            c = self.conn.cursor()

            try:
                if args == None:
                    c.execute(statement)
                else:
                    c.execute(statement, args)
                self.conn.commit()
                last_id = c.lastrowid
                c.close()
                return last_id

            except Exception as e:
                self.conn.rollback()
                c.close()
                raise e

    def exec_select(self, statement, args=None):
        with self.conn:
            c = self.conn.cursor()

            try:
                if args == None:
                    c.execute(statement)
                else:
                    c.execute(statement, args)
                self.conn.commit()
                r = c.fetchall()
                c.close()
                return r

            except Exception as e:
                self.conn.rollback()
                c.close()
                raise e

    def exec_file(self, filename: str, skip_error: bool = False):
        """
        Read and execute a '.sql' file.
        :param filename: SQL file.
        :param skip_error: Skip command error.
        """
        # Read file
        with open(filename, 'r') as fd:
            sql = fd.read()

        with self.conn:
            c = self.conn.cursor()
            for command in sql.split(';'):
                try:
                    c.execute(command)
                except Exception as e:
                    if skip_error:
                        print("Command skipped: %s" % str(e))
                    else:
                        self.conn.rollback()
                        raise e
            self.conn.commit()
