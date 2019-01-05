from typing import Dict, Any

import discord
from discord.ext import commands

from .state import VoiceState


class VoiceStateController:

    voice_states: Dict[str, VoiceState]

    def __init__(self, bot: commands.Bot):
        """
        VoiceState controller
        :param bot:
        """
        # Bot instance
        self.bot = bot

        # Control bot in multiple servers
        self.voice_states = {}

    def get_voice_state(self, server: discord.Server) -> VoiceState:
        """
        Get the server's VoiceState
        :param server:
        :return:
        """
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state
        return state

    async def create_voice_client(self, channel: discord.Channel):
        """
        Connect to the channel and create a VoiceState
        :param channel:
        :return:
        """
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def unload(self):
        """
        Stop all VoiceState
        :return:
        """
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass
