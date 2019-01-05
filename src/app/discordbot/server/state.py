import discord
from discord.ext import commands

from ..server.behavior.voice.state import VoiceState
from ...localmusic import LocalMusicController


class ServerState:
    def __init__(self, bot: commands.Bot, musics: LocalMusicController = None):
        """
        ServerState
        :param bot:
        """
        self.bot = bot                              # type: commands.Bot
        self.voice = VoiceState(self.bot, musics)   # type: VoiceState

    async def summon(self, channel: discord.Channel):
        """
        Connect to the channel
        :param channel:
        :return:
        """
        if self.voice.is_connected():
            await self.voice.move_to(channel)
        else:
            await self.voice.connect(channel)

    def unload(self):
        self.voice.unload()
