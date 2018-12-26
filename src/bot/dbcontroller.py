import re
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from utils.singleton import Singleton
from utils.db import Database


class DBController(metaclass=Singleton):

    def __init__(self):
        self.db = None  # type: Database
        self.num_animes = 0
        self.num_musics = 0

    def __sanitize(self, s):
        return s.replace('-', ' ').replace('!', '').replace('?', '')

    def set_db(self, db: Database):
        self.db = db
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT count(*) FROM anime")
        self.num_animes = int(cursor.fetchone()[0])
        cursor.execute("SELECT count(*) FROM music")
        self.num_musics = int(cursor.fetchone()[0])
        cursor.close()

    def search_music(self, search: str):
        search = self.__sanitize(search)
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                        SELECT anime_music.*, music.id
                            FROM anime_music
                        INNER JOIN music
                            ON anime_music.folder LIKE music.filename
                        WHERE anime_music MATCH ?
                        ORDER BY music.id
                        LIMIT 20""", (search,))
            while True:
                music_data = cursor.fetchone()
                if music_data is None:
                    break

                yield {
                    'anime': music_data[0],
                    'ref': music_data[1],
                    'music': music_data[2],
                    'artists': music_data[3],
                    'folder': music_data[4],
                    'id': music_data[5]
                }
        finally:
            cursor.close()

    def create_mp3_player(self, state, search, **kwargs):
        search = self.__sanitize(search)
        cursor = self.db.conn.cursor()
        try:

            if re.search('^[0-9]+$', search):
                # Search song by ID
                cursor.execute("""
                    SELECT anime_music.*, music.id
                        FROM anime_music
                    INNER JOIN music
                        ON anime_music.folder LIKE music.filename
                    WHERE music.id = (?)
                    LIMIT 1""", (int(search),))
            else:
                # Search song by name
                cursor.execute("""
                    SELECT anime_music.*, music.id
                        FROM anime_music
                    INNER JOIN music
                        ON anime_music.folder LIKE music.filename
                    WHERE anime_music MATCH (?)
                    ORDER BY rank
                    LIMIT 1""", (search,))

            # Get result
            music_data = cursor.fetchone()
            cursor.close()
            cursor = None

            mp3 = MP3(music_data[4])
            player = state.voice.create_ffmpeg_player(music_data[4], after=state.toggle_next)
            player.title = "[{0[5]}] {0[2]} ({0[1]})".format(music_data)
            player.artist = ' & '.join(music_data[3].split('/'))
            player.duration = mp3.info.length if mp3 else 0

            return player

        except Exception as e:
            if cursor is not None:
                cursor.close()
            print("Error in DBController create_mp3_player: \n" + str(e))
