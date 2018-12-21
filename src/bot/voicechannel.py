import asyncio
import discord
from discord.ext import commands
from typing import Union, Any

from .request import YTRequest, MP3Request

# ==================================================================================================================== #


class VoiceStateFactory:

    def __init__(self, bot: commands.Bot):
        # Bot instance
        self.bot = bot

        # Control bot in multiple servers
        self.voice_states = {}

    def get_voice_state(self, server: discord.Server):
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
        state.voice = voice  # type: discord.VoiceClient

    def unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

# ==================================================================================================================== #


class VoiceState:

    def __init__(self, bot: commands.Bot):

        self.current = None     # type: Union[YTRequest, MP3Request]
        self.voice = None       # type: discord.VoiceClient
        self.autoplay = None    # type: Request
        self.volume = 0.3       # type: float

        # instance of the bot
        self.bot = bot

        # flag to access songs queue
        self.play_next_song = asyncio.Event()
        # songs queue
        self.songs = asyncio.Queue()

        # a set of user_ids that voted
        self.skip_votes = set()

        # thread: wait songs
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    # ---------------------------------------------------------------------------------------------------------------- #

    async def request_song(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        # Create a request
        if hasattr(player, 'yt'):
            entry = YTRequest(message, player)
        else:
            entry = MP3Request(message, player)

        # Playing a songs?
        if not self.songs.empty() or self.is_playing():
            entry.enqueded_msg = await self.bot.send_message(message.channel, '```Enqueued ' + str(entry) + "```")

        # Save the request
        await self.songs.put(entry)

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        player = self.current.player
        return not player.is_done()

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    @property
    def player(self):
        return self.current.player

    # ---------------------------------------------------------------------------------------------------------------- #

    async def audio_player_task(self):
        while True:
            try:
                # CLEAR next song flag
                self.play_next_song.clear()

                # Get next song or wait
                self.current = await self.songs.get()  # type: Union[YTRequest, MP3Request]

                embed = self.current.message_playing()

                await self.bot.delete_message(self.current.message)
                if self.current.enqueued_message is not None:
                    await self.bot.delete_message(self.current.enqueued_message)
                msg = await self.bot.send_message(self.current.message.channel, embed=embed)  # type: discord.Message

                self.current.player.volume = self.volume
                self.current.player.start()

                # WAIT next song flag
                await self.play_next_song.wait()
                await self.bot.delete_message(msg)
            except Exception as e:
                print("Error in VoiceState 'audio_player_task' thread: \n" + str(e))

    # ---------------------------------------------------------------------------------------------------------------- #

# ==================================================================================================================== #
