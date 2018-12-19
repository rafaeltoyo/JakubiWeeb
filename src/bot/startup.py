import os
import discord
from discord.ext import commands

from utils.config import Config
from utils.db import Database
from utils.loader.loader import FileLoader

from model.anime import Anime
from model.music import Music

from bot import Jakubiweeb


def startup():
    if not discord.opus.is_loaded():
        # the 'opus' library here is opus.dll on windows
        # or libopus.so on linux in the current directory
        # you should replace this with the location the
        # opus library is located in and with the proper filename.
        # note that on windows this DLL is automatically provided for you
        # https://discordpy.readthedocs.io/en/latest/api.html#embed

        discord.opus.load_opus('opus')

    config = Config(project="JakubiWeeb", filename="config.json")
    database = Database(config=config, filename="database.db")

    cursor = database.conn.cursor()

    animes = {}

    cursor.execute("SELECT * FROM anime")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        print(row)
        animes[row[0]] = Anime(name=row[1], folder=row[2])

    cursor.execute("SELECT * FROM music")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        animes[row[3]].append(Music(title=row[1], filename=row[2]))

    cursor.close()
    print(''.join([str(animes[a]) + '\n' for a in animes]))

    bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.config.bot_prefix),
                       description='Bem entendido isso? Resolve o Cascode ai ...')
    bot.add_cog(Jakubiweeb(bot))

    @bot.event
    async def on_ready():
        print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

    bot.run(config.config.bot_token)


def startup_init():
    config = Config(project="JakubiWeeb", filename="config.json")
    database = Database(config=config, filename="database.db")
    database.create(config.projectpath + "sql" + os.path.sep + "createdb.sql")

    cursor = database.conn.cursor()

    fileloader = FileLoader(path=config.config.music_folder)
    for anime in fileloader.search_animes():
        cursor.execute("""
        INSERT 
            INTO anime (title, folder) 
            VALUES (?, ?)""", (anime.name, anime.folder))
        anime_id = cursor.lastrowid
        for music in anime:
            cursor.execute("""
            INSERT 
                INTO music (title, filename, fk_music_anime_id) 
                VALUES (?, ?, ?)""", (music.title, music.filename, anime_id))
            # mp3 = MP3(music.filename)
            # print(music.title)
            # print(mp3.get('TIT2'))
            # print(mp3.get('TPE1'))
    cursor.execute("SELECT * FROM anime")
    print(cursor.fetchall())
    cursor.execute("SELECT * FROM music")
    print(cursor.fetchall())
    database.conn.commit()
