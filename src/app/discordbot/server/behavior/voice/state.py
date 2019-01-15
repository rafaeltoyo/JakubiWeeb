import numpy as np
import random as rnd
import asyncio

import discord
from discord.ext import commands

from .request import Request, YTRequest, LMRequest
from ....enums import *
from ....utils import *
from .....localmusic import LocalMusicController
from ....utils.queue import MusicQueue


class VoiceState:

    # ================================================================================================================ #
    #   Constructor
    # ---------------------------------------------------------------------------------------------------------------- #

    def __init__(self, bot: commands.Bot, musics: LocalMusicController = None):
        """
        Voice State:
        When the bot connect in some server, we create a state for this server.
        :param bot:
        """

        # ------------------------------------------------------------------------------------------------------------ #
        #   External objects

        # bot instance
        self.bot = bot
        # local music controller
        self.musics = musics  # type: LocalMusicController

        # ------------------------------------------------------------------------------------------------------------ #
        #   Control parameters

        # Voice client
        self.__voice = None  # type: discord.VoiceClient

        # Current request (now playing)
        self.__current = None  # type: Request

        # Autoplay request
        self.__autoplay = None

        # Song volume
        self.__volume = 0.3

        # ------------------------------------------------------------------------------------------------------------ #
        #   Song queue variables

        # flag to access songs queue
        self.play_next_song = asyncio.Event()
        # songs queue
        self.songs = asyncio.Queue()
        # a set of user_ids that voted
        self.skip_votes = set()

        # ------------------------------------------------------------------------------------------------------------ #
        #   Audio Player Task
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

        #------------------------------------------------------------------------------------------------------------- #
        #   Txt queue
        self.queue = MusicQueue()

    def unload(self):
        if self.is_connected():
            self.bot.loop.create_task(self.__voice.disconnect())
        self.audio_player.cancel()

    # ================================================================================================================ #
    #   Voice Client
    # ---------------------------------------------------------------------------------------------------------------- #

    async def connect(self, channel: discord.Channel):
        self.__voice = await self.bot.join_voice_channel(channel)

    async def move_to(self, channel: discord.Channel):
        await self.__voice.move_to(channel)

    def is_connected(self):
        return self.__voice is not None

    async def disconnect(self):
        if self.is_connected():
            # Stop music
            self.stop()
            # Stop audio player task
            self.audio_player.cancel()
            # Disconnect VoiceClient
            await self.__voice.disconnect()

    # ================================================================================================================ #
    #   Audio Player configuration
    # ---------------------------------------------------------------------------------------------------------------- #

    @property
    def player(self):
        return self.__current.player

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, v: float):
        if 0 < v < 1:
            self.__volume = v

    def current_song(self):
        if self.is_playing():
            return self.player.search
        return ""

    def is_playing(self):
        if self.__voice is None or self.__current is None:
            return False
        return not self.player.is_done()

    def pause(self):
        if self.is_playing():
            self.player.pause()
            return True
        return False

    def resume(self):
        if self.is_playing():
            self.player.resume()
            return True
        return False

    def stop(self):
        if self.is_playing():
            self.player.stop()
            return True
        return False

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    # ================================================================================================================ #
    #   Audio Player user functions
    # ---------------------------------------------------------------------------------------------------------------- #

    async def request_song(self, message: discord.Message, player: discord.voice_client.StreamPlayer):

        # Create a request
        if hasattr(player, 'yt'):
            entry = YTRequest(message, player)
        else:
            entry = LMRequest(message, player)

        # Playing a songs?
        if not self.songs.empty() or self.is_playing():
            entry.enqueued_message = await self.bot.send_message(message.channel, embed=entry.message_enqueued())

        # Save the request
        await self.songs.put(entry)

    async def fn_request_yt_song(self, message: discord.Message, search: str):
        """
        Request a song with YoutubeDL
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        :param message: Requester message
        :param search: Requested song
        :return: Success
        """
        opts = {'default_search': 'auto', 'quiet': True}

        try:
            player = await self.__voice.create_ytdl_player(search, ytdl_options=opts, after=self.toggle_next)
            player.search = player.title
        except Exception as e:
            error = "An error occurred while processing this request: ```py\n{}: {}\n```".format(type(e).__name__, e)
            await self.bot.send_message(message.channel, embed=MessageBuilder.create_error(error))
            return False

        self.queue.add_music(search) # Adiciona ao txt

        await self.request_song(message, player)
        return True

    async def fn_request_local_song(self, message: discord.Message, search: str):
        """
        Request a song from SQLite3 database
        :param message: Requester message
        :param search: Requested song
        :return: Success
        """
        if self.musics is None or self.musics.num_music <= 0:
            await self.bot.send_message(message.channel, embed=MessageBuilder.create_error(EnumMessages.ERROR_MSC_CTRL))
            return

        try:
            music = self.musics.search(search)
            if music is None:
                raise LocalMusicNotFoundException()
            player = self.__voice.create_ffmpeg_player(music.filename, after=self.toggle_next)
            player.title = music.full_title
            player.artist = music.artists
            player.duration = music.duration
            player.search = music.name + " " + music.artists
        except Exception as e:
            error = "An error occurred while processing this request: ```py\n{}: {}\n```".format(type(e).__name__, e)
            await self.bot.send_message(message.channel, embed=MessageBuilder.create_error(error))
            return False

        self.queue.add_music(search)  # Adiciona ao txt

        await self.request_song(message, player)
        return True

    async def fn_request_random_local_song(self, message: discord.Message):
        """
        Request a random song from SQLite3 database
        :param message: Requester message
        :param search: Requested song
        :return: Success
        """
        if self.musics is None or self.musics.num_music <= 0:
            await self.bot.send_message(message.channel, embed=MessageBuilder.create_error(EnumMessages.ERROR_MSC_CTRL))
            return
        await self.fn_request_local_song(message, str(rnd.randint(1, self.musics.num_music)))

    async def fn_autoplay(self, message: discord.Message):
        if self.musics is None or self.musics.num_music <= 0:
            await self.bot.send_message(message.channel, embed=MessageBuilder.create_error(EnumMessages.ERROR_MSC_CTRL))
            return

        if self.__autoplay is not None:
            # Already auto playing songs
            if message.author.id == self.__autoplay.author.id:
                # If same author then turn-off the autoplay
                pass
            try:
                await self.bot.delete_message(self.__autoplay)
            finally:
                self.__autoplay = None
            embed = MessageBuilder.create_base_message(
                title=EnumMessages.TITLE_AUTOPLAY_OFF,
                content=EnumMessages.CONTENT_AUTOPLAY_OFF,
                color=discord.Color.dark_red())
            await self.bot.send_message(message.channel, embed=embed)
        else:
            # Turn-on autoplay
            self.__autoplay = message
            embed = MessageBuilder.create_base_message(
                title=EnumMessages.TITLE_AUTOPLAY_ON,
                content=EnumMessages.CONTENT_AUTOPLAY_ON,
                color=discord.Color.dark_blue())
            await self.bot.send_message(message.channel, embed=embed)
            await self.__prepare_autoplay()

    async def fn_skip_song(self, message: discord.Message):

        # FIXME: Create skip handler class
        skip_nedded = max(0, min(1, np.ceil(len(message.server.members) / 2.0)))

        if not self.is_playing():
            # Not playing any music right now
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_WTOUT_MS))
            return

        # Skipping music
        # Get skip author
        voter = message.author

        if voter == self.__current.message.author:
            # Requester requested skipping song
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_REQ_SKIP))

            self.queue.skip_music() # Tira o primeiro índice da lista de queue

            self.skip()
        elif voter.id not in self.skip_votes:
            # You have not voted yet
            self.skip_votes.add(voter.id)
            total_votes = len(self.skip_votes)
            if total_votes >= skip_nedded:
                # Skip vote passed, skipping song
                self.queue.skip_music()  # Tira o primeiro índice da lista de queue
                await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_VOT_SKIP))
            else:
                # Needs more vote
                await self.bot.say(embed=MessageBuilder.create_simple_info(
                    EnumMessages.CONTENT_SKIP_VOT_WAIT.format(total_votes, skip_nedded)))
        else:
            # You have already voted to skip this song
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_ALRD_VOT))

    async def fn_now_playing(self):
        if self.is_playing():
            await self.bot.say(embed=self.__current.message_playing())
        else:
            await self.bot.say(embed=MessageBuilder.create_alert(EnumMessages.CONTENT_SKIP_WTOUT_MS))

    # ================================================================================================================ #
    #   Audio Player behavior
    # ---------------------------------------------------------------------------------------------------------------- #

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def __prepare_autoplay(self):
        # Empty songs queue and autoplay active?
        if self.songs.empty() and self.__autoplay is not None and not self.is_playing():
            # Request a random song
            await self.fn_request_random_local_song(self.__autoplay)

    async def __prepare_song(self) -> Request:
        # Empty songs queue and autoplay active?
        await self.__prepare_autoplay()

        current = await self.songs.get()  # type: Request

        # check if exists and delete "enqueued" message
        if current.enqueued_message is not None:
            await self.bot.delete_message(current.enqueued_message)

        # delete request message
        if self.__autoplay is None or self.__autoplay.id != current.message.id:
            await self.bot.delete_message(current.message)

        # set user volume
        current.player.volume = self.__volume

        return current

    async def audio_player_task(self):
        while True:
            try:
                """ clear flag """
                self.play_next_song.clear()

                self.__current = await self.__prepare_song()  # type: Request

                # build "playing" message
                embed = self.__current.message_playing()
                msg = await self.bot.send_message(self.__current.message.channel, embed=embed)

                # start music
                self.__current.player.start()

                """ wait flag """
                await self.play_next_song.wait()

                # delete "playing" message
                try:
                    await self.bot.delete_message(msg)
                except:
                    pass
            except asyncio.CancelledError as e:
                return
            except Exception as e:
                print("Error in VoiceState 'audio_player_task' thread: ```py\n{}: {}\n```".format(type(e).__name__, e))
                self.__autoplay = None

# ================================================================================================================ #
