from typing import Dict

import discord
from discord.ext import commands

from ..server.state import ServerState
from ...localmusic import LocalMusicController


class ServerController:

    __states: Dict[str, ServerState]

    def __init__(self, bot: commands.Bot, musics: LocalMusicController = None):
        """
        ServerState controller
        :param bot:
        """
        # Bot instance
        self.__bot = bot
        self.__musics = musics

        # Control bot in multiple servers
        self.__states = {}

    def get(self, server: discord.Server) -> ServerState:
        """
        Recover the server state
        :param server: Discord server
        :return: ServerState
        """
        state = self.__states.get(server.id)
        if state is None:
            state = ServerState(server, self.__bot, self.__musics)
            self.__states[server.id] = state
        return state

    async def disconnect(self, server: discord.Server):
        """
        Disconnect and delete server state
        :param server: Discord server
        :return: Nothing
        """
        state = self.__states.get(server.id)
        del self.__states[server.id]
        await state.voice.disconnect()

    def unload(self):
        """
        Stop all VoiceState
        :return:
        """
        for state in self.__states.values():
            try:
                state.unload()
            except:
                pass
