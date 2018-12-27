import sys
import os

import discord
from discord.ext import commands
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from utils.config import Config
from utils.db import Database
from utils.loader import FileLoader
from utils.log import Log

from model.anime import Anime
from model.music import Music

from bot import Jakubiweeb


class Controller(object):

    # ================================================================================================================ #
    #   Initialize
    # ================================================================================================================ #

    def __init__(self, *args):
        """
        Main controller.
        :param args: Sys args
        """

        try:
            # Load/Create the configuration file and configure the log.
            self.cf = Config(project="JakubiWeeb", filename="config.json")
        except Exception as e:
            # We need the configuration and log to continue ...
            print("Unable to start the program: " + str(e))
            exit(-1)

        # Start log controller.
        self.__start_log()

        # Start database connection.
        self.db = Database(config=self.cf, filename="database.db")

        # Parse the arguments in terminal
        self.__parse_cmd(*args)

    # ---------------------------------------------------------------------------------------------------------------- #

    def __start_log(self):
        """
        Start and configure log class.
        """
        Log().set_config(self.cf)
        # noinspection PyBroadException
        try:
            # Try to write a dummy message.
            Log().write("Initializing ...")
        except:
            # Use terminal as output.
            Log().set_debug()

    # ---------------------------------------------------------------------------------------------------------------- #

    def __parse_cmd(self, *args):
        """
        Parse arguments to execute commands in database.
        :param args: User input in terminal.
        """
        create = False
        delete = False

        # Checking number of arguments.
        if len(args) > 0:
            Log().write("Arguments: [" + ', '.join(args) + ']')

        # Checking invalid arguments.
        for arg in args:
            if arg == "reset":
                create = True
                delete = True
            elif arg == "init":
                create = True
            elif arg == "clean":
                delete = True
            else:
                Log().err("Invalid argument '{}'!".format(arg))

        # Executing commands based in arguments
        try:
            if delete:
                self.__delete_db()
            if create:
                self.__create_db()
                self.__create_monolith()
        except Exception as e:
            Log().err("Initializing error: " + str(e))

    # ================================================================================================================ #
    #   Stop
    # ================================================================================================================ #

    def __del__(self):
        """
        Delete all controllers inside
        """
        Log().write("Stopping ...")
        del self.cf
        del self.db

    # ================================================================================================================ #
    #   Delete database
    # ================================================================================================================ #

    def __delete_db(self):
        """
        Delete database with 'deletedb.sql' file.
        :return:
        """
        Log().write("Deleting the database ...")
        self.db.exec(self.cf.projectpath + "sql" + os.path.sep + "deletedb.sql")

    # ================================================================================================================ #
    #   Create and populate database
    # ================================================================================================================ #

    def __create_db(self):
        """
        Create database with 'createdb.sql' file.
        :return:
        """
        Log().write("Creating the database ...")
        self.db.exec(self.cf.projectpath + "sql" + os.path.sep + "createdb.sql")
        cursor = self.db.conn.cursor()

        # Load music folder
        loader = FileLoader(path=self.cf.config.music_folder)

        for anime in loader.search_animes():
            try:
                cursor.execute(
                    """INSERT OR REPLACE INTO anime (title, folder) VALUES (?, ?)""",
                    (anime.name, anime.folder))
            except Exception as e:
                Log().err("Insert error in '{}': ".format(anime.name) + str(e))
                continue
            anime_id = cursor.lastrowid

            for music in anime:
                try:
                    cursor.execute(
                        """INSERT OR REPLACE INTO music (title, filename, fk_music_anime_id) VALUES (?, ?, ?)""",
                        (music.title, music.filename, anime_id))
                except Exception as e:
                    Log().err("Insert error in '{}' (anime: {}): ".format(music.title, anime.name) + str(e))

        self.db.conn.commit()

    # ================================================================================================================ #
    #   Load all data in database as anime array
    # ================================================================================================================ #

    def __load_db(self):

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
        # print(''.join([str(animes[a]) + '\n' for a in animes]))
        return animes

    # ================================================================================================================ #
    #   Create a fts5 table with all data in database
    # ================================================================================================================ #

    def __create_monolith(self):
        try:
            animes = self.__load_db()
        except Exception as e:
            Log().err("Error in load db: " + str(e))
            return

        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS anime_music 
            USING FTS5(anime, ref, music, artists, folder)
            """)

        for kanime in animes:
            anime = animes[kanime]
            for music in anime:
                try:
                    info = self.__extract_info(music)
                    if len(info) != 2 or info[0] == '' and info[1] == '':
                        continue

                    cursor.execute(
                        """INSERT INTO anime_music (anime, ref, music, artists, folder) VALUES (?, ?, ?, ?, ?)""",
                        (str(anime.name), str(music.title), info[0], info[1], str(music.filename)))
                except Exception as e:
                    Log().err("Insert error in monolith '{}' (anime: {}): ".format(music.title, anime.name) + str(e))

        self.db.conn.commit()

    def __extract_info(self, music: Music):
        """
        Get music file info
        :param music: filename
        :return: music name, artists
        """
        basename, extension = os.path.splitext(music.filename)

        if basename == '' and extension == '':
            return ['', '']
        extension = extension.replace('.', '')

        if extension == 'mp3':
            # MP3
            mp3 = MP3(music.filename)
            if mp3 is None or 'TIT2' not in mp3.keys() or 'TPE1' not in mp3.keys():
                return ['', '']
            return [str(mp3.get('TIT2')), str(mp3.get('TPE1'))]

        elif extension in ['m4a', 'mp4']:
            # MPEG4
            mp4 = MP4(music.filename)
            if mp4 is None or '©nam' not in mp4.keys() or '©ART' not in mp4.keys():
                return ['', '']
            return [str(mp4.get('©nam')), str(mp4.get('©ART'))]

        elif extension == 'flac':
            # FLAC
            flac = FLAC(music.filename)
            if flac is None or 'title' not in flac.keys() or 'artists' not in flac.keys():
                return ['', '']
            return [str(flac.get('title')), str(flac.get('artists'))]

        return ['', '']

    # ================================================================================================================ #
    #   Run the bot
    # ================================================================================================================ #

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
            Log().write("Initialized!")
            print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

        bot.run(self.cf.config.bot_token)

    # ================================================================================================================ #
