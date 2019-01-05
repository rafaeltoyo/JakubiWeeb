from .model import Music
from .exceptions import *

from utils.filesystem import *
from utils.db.database import Database


class LocalMusicStorage:
    _db: Database

    class __MusicDAO:

        def __init__(self, db: Database):
            self.__db = db

        def create(self):
            c = self.__db.exec_sql("""
            CREATE TABLE IF NOT EXISTS music (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                filename TEXT NOT NULL UNIQUE,
                artists TEXT,
                nickname TEXT,
                duration INT,
                fk_music_folder_id INTEGER NOT NULL,
                FOREIGN KEY(fk_music_folder_id) REFERENCES folder(id)
            )
            """)
            c.close()

        def select(self):
            return self.__db.exec_select("""
            SELECT * FROM music
            """)

        def count(self):
            return self.__db.exec_select("""
            SELECT count(*) FROM music
            """)

        def insert(self, music: Music, folder_id: int):
            return self.__db.exec_insert("""
            INSERT INTO music(name, filename, artists, nickname, duration, fk_music_folder_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (music.name, music.filename, music.artists, music.title, music.duration, folder_id,))

        def delete(self, music_id: int):
            c = self.__db.exec_sql("""
            DELETE FROM music
            WHERE id = ?
            """, (music_id,))
            c.close()
            self.__db.conn.commit()

    class __FolderDAO:

        def __init__(self, db: Database):
            self.__db = db

        def create(self):
            c = self.__db.exec_sql("""
            CREATE TABLE IF NOT EXISTS folder (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                path TEXT NOT NULL UNIQUE
            )
            """)
            c.close()

        def select(self, name=None):
            if name is not None:
                r = self.__db.exec_select("""
                SELECT * FROM folder WHERE name like ?
                """, (name,))
                if isinstance(r, list) and len(r) > 0:
                    return r[0]
                else:
                    return None
            else:
                return self.__db.exec_select("""
                SELECT * FROM folder
                """)

        def count(self):
            return self.__db.exec_select("""
            SELECT count(*) FROM folder
            """)

        def insert(self, name: str, folder: str):
            return self.__db.exec_insert("""
            INSERT INTO folder(name, path)
            VALUES (?, ?)
            """, (name, folder,))

        def update(self, name: str, path: str):
            c = self.__db.exec_sql("""
            UPDATE folder SET
                path = ?
            WHERE name = ?
            """, (path, name,))
            c.close()
            self.__db.conn.commit()

        def delete(self, folder_id: int):
            c = self.__db.exec_sql("""
            DELETE FROM folder
            WHERE id = ?
            """, (folder_id,))
            c.close()
            self.__db.conn.commit()

    class __SearchToolDAO:

        def __init__(self, db: Database):
            self.__db = db

        def __sanitize(self, s):
            return s.replace('-', ' ').replace('!', '').replace('?', '')

        def select(self, search=None, num: int = 1):
            query = ""

            # Validate search parameter
            if isinstance(search, str):
                search = self.__sanitize(search)
                query = """
                SELECT
                    music.id,
                    music.name,
                    music.filename,
                    music.artists,
                    music.nickname,
                    music.duration
                FROM search_tool
                INNER JOIN music
                    ON search_tool.filename LIKE music.filename
                WHERE search_tool MATCH ?
                """
                if num == 1:
                    query += """
                    ORDER BY rank
                    LIMIT 1
                    """
                else:
                    query += """
                    ORDER BY music.id
                    LIMIT {}
                    """.format(num)

            elif isinstance(search, int):
                query = """
                SELECT
                    music.id,
                    music.name,
                    music.filename,
                    music.artists,
                    music.nickname,
                    music.duration
                FROM music
                WHERE music.id = ?
                """
            else:
                raise LMInvalidSearchParameter()

            cursor = self.__db.conn.cursor()
            try:
                cursor.execute(query, (search,))
                while True:
                    music_data = cursor.fetchone()
                    if music_data is None:
                        break

                    yield {
                        'idt': int(music_data[0]),
                        'name': str(music_data[1]),
                        'filename': str(music_data[2]),
                        'artists': str(music_data[3]),
                        'title': str(music_data[4]),
                        'duration': float(music_data[5])
                    }
            finally:
                cursor.close()

        def create(self):
            with self.__db.conn:
                c = self.__db.conn.cursor()
                print("Creating search tool ...")

                try:
                    c.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS search_tool 
                    USING FTS5(name, filename, artists, nickname, folder)
                    """)
                    c.execute("""DELETE FROM search_tool""")
                    print("Table created!")

                    c.execute("""
                    SELECT 
                        music.name as name, 
                        music.filename as filename, 
                        music.artists as artists, 
                        music.nickname as nickname,
                        folder.name as folder
                    FROM music
                    INNER JOIN folder
                        ON music.fk_music_folder_id = folder.id
                    """)

                    content = []
                    for row in c.fetchall():
                        c.execute("""
                        INSERT INTO search_tool(name, filename, artists, nickname, folder)
                        VALUES (?, ?, ?, ?, ?)
                        """, (*row,))
                    print("Search tool data inserted!")

                    self.__db.conn.commit()
                    c.close()
                except Exception as e:
                    self.__db.conn.rollback()
                    c.close()
                    raise e

    def __init__(self, error_handler=None):
        """
        Music object DAO.
        :param error_handler:
        """
        try:
            self.db = Database(PathBuilder().db_file)
            self.folderDAO = LocalMusicStorage.__FolderDAO(self.db)
            self.musicDAO = LocalMusicStorage.__MusicDAO(self.db)
            self.searchToolDAO = LocalMusicStorage.__SearchToolDAO(self.db)
        except Exception as e:
            if error_handler is None:
                raise LMCreateConnectionException(e)
            else:
                self.db = None
                error_handler(LMCreateConnectionException(e))

    def is_connected(self):
        return self.db is not None and self.db.conn is not None
