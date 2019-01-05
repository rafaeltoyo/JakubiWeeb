import discord
from discord.ext import commands

from ..server.controller import ServerController
from ...config import Config
from ...localmusic import LocalMusicController


class DiscordApplication:

    def __init__(self, config: Config, musics: LocalMusicController):
        """
        Discord application
        """
        self.__bot = None
        self.__controller = None
        self.__config = config
        self.__musics = musics

    @property
    def bot(self) -> commands.Bot:
        return self.__bot

    @property
    def states(self) -> ServerController:
        return self.__controller

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def musics(self) -> LocalMusicController:
        return self.__musics

    def run(self):
        """
        Launch the discord application
        :return:
        """
        if not discord.opus.is_loaded():
            # the 'opus' library here is opus.dll on windows
            # or libopus.so on linux in the current directory
            # you should replace this with the location the
            # opus library is located in and with the proper filename.
            # note that on windows this DLL is automatically provided for you
            # https://discordpy.readthedocs.io/en/latest/api.html#embed

            discord.opus.load_opus('opus')

        self.__bot = commands.Bot(command_prefix=commands.when_mentioned_or(self.config.params.bot_prefix),
                           description='Bem entendido isso? Resolve o Cascode ai ...')
        self.__bot.add_cog(self)

        @self.__bot.event
        async def on_ready():
            # Log().write("Initialized!")
            print('Logged in as:\n{0} (ID: {0.id})'.format(self.__bot.user))

        self.__controller = ServerController(self.__bot, self.__musics)
        self.__bot.run(self.config.params.bot_token)
