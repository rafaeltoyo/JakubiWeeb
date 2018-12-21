import os
import discord
from discord.ext import commands
from mutagen.mp3 import MP3

from utils.config import Config
from utils.db import Database
from utils.loader import FileLoader

from model.anime import Anime
from model.music import Music

from bot.dbcontroller import DBController
from bot import Jakubiweeb


class Controller(object):

    def __init__(self):

        self.cf = Config(project="JakubiWeeb", filename="config.json")
        self.db = Database(config=self.cf, filename="database.db")
        DBController().set_db(self.db)

    def __del__(self):

        del self.cf
        del self.db

    def create_database(self):

        self.db.create(self.cf.projectpath + "sql" + os.path.sep + "createdb.sql")
        cursor = self.db.conn.cursor()

        fileloader = FileLoader(path=self.cf.config.music_folder)

        for anime in fileloader.search_animes():
            cursor.execute("""
                INSERT OR REPLACE
                    INTO anime (title, folder) 
                    VALUES (?, ?)""", (anime.name, anime.folder))

            anime_id = cursor.lastrowid

            for music in anime:
                cursor.execute("""
                    INSERT OR REPLACE
                        INTO music (title, filename, fk_music_anime_id) 
                        VALUES (?, ?, ?)""", (music.title, music.filename, anime_id))

        self.db.conn.commit()

    def load_database(self):

        cursor = self.db.conn.cursor()

        animes = {}

        cursor.execute("SELECT * FROM anime")
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            animes[row[0]] = Anime(name=row[1], folder=row[2])

        cursor.execute("SELECT * FROM music")
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            animes[row[3]].append(Music(title=row[1], filename=row[2]))

        cursor.close()
        print(''.join([str(animes[a]) + '\n' for a in animes]))
        return animes

    def create_monolith(self):

        animes = self.load_database()

        cursor = self.db.conn.cursor()

        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS 
                anime_music
            USING FTS5(anime, ref, music, artirts, folder)
            """)

        for kanime in animes:
            anime = animes[kanime]

            for music in anime:

                mp3 = MP3(music.filename)
                if mp3 is None:
                    continue

                cursor.execute("""
                    INSERT INTO anime_music (anime, ref, music, artirts, folder)
                        VALUES (?, ?, ?, ?, ?)""",
                               (str(anime.name), str(music.title), str(mp3.get('TIT2')), str(mp3.get('TPE1')),
                                str(music.filename)))

        self.db.conn.commit()

    def run(self):

        if not discord.opus.is_loaded():
            # the 'opus' library here is opus.dll on windows
            # or libopus.so on linux in the current directory
            # you should replace this with the location the
            # opus library is located in and with the proper filename.
            # note that on windows this DLL is automatically provided for you
            # https://discordpy.readthedocs.io/en/latest/api.html#embed

            discord.opus.load_opus('opus')

        bot = commands.Bot(command_prefix=commands.when_mentioned_or(self.cf.config.bot_prefix),
                           description='Bem entendido isso? Resolve o Cascode ai ...')
        bot.add_cog(Jakubiweeb(bot, self.cf, self.db))

        @bot.event
        async def on_ready():
            print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

        bot.run(self.cf.config.bot_token)
