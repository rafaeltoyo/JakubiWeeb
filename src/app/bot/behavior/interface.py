import discord
from discord.ext import commands
from app.application import Application


class CommandsInterface:

    bot: commands.Bot

    def __init__(self, app: Application):
        # Save the application to access configuration parameters and database
        self.__app = app
        self.bot = None

    @property
    def config(self):
        return self.__app.config

    @property
    def musics(self):
        return self.__app.music

    def run(self):
        if not discord.opus.is_loaded():
            # the 'opus' library here is opus.dll on windows
            # or libopus.so on linux in the current directory
            # you should replace this with the location the
            # opus library is located in and with the proper filename.
            # note that on windows this DLL is automatically provided for you
            # https://discordpy.readthedocs.io/en/latest/api.html#embed

            discord.opus.load_opus('opus')

        bot = commands.Bot(command_prefix=commands.when_mentioned_or(self.config.params.bot_prefix),
                           description='Bem entendido isso? Resolve o Cascode ai ...')
        self.bot = bot
        bot.add_cog(self)

        @bot.event
        async def on_ready():
            # Log().write("Initialized!")
            print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

        bot.run(self.config.params.bot_token)
