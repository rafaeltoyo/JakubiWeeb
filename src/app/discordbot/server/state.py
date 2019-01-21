import discord
from discord.ext import commands

from ..server.behavior.voice.state import VoiceState
from ...localmusic import LocalMusicController


class ServerState:
    def __init__(self, server: discord.Server, bot: commands.Bot, musics: LocalMusicController = None):
        """
        ServerState
        :param bot:
        """
        self.server: discord.Server = server
        self.bot: commands.Bot = bot
        self.voice: VoiceState = VoiceState(server, self.bot, musics)

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
