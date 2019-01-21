import numpy as np
import random as rnd
import asyncio

import discord
from discord.ext import commands

from .queue import SongQueue
from .request import Request, YTRequest, LMRequest
from ....enums import *
from ....utils import *
from .....localmusic import LocalMusicController


class VoiceState:

    # ================================================================================================================ #
    #   Constructor
    # ---------------------------------------------------------------------------------------------------------------- #

    def __init__(self, server: discord.Server, bot: commands.Bot, musics: LocalMusicController = None):
        """
        Voice State:
        When the bot connect in some server, we create a state for this server.
        :param bot:
        """

        # ------------------------------------------------------------------------------------------------------------ #
        #   External objects

        # state server
        self.server = server
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
        self.songs = SongQueue()

        # ------------------------------------------------------------------------------------------------------------ #
        #   Skip

        # a set of user_ids that voted
        self.skip_votes = set()
        # skip set locker
        self.__skip_lock = asyncio.Lock()

        # ------------------------------------------------------------------------------------------------------------ #
        #   Audio Player Task
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

        # ------------------------------------------------------------------------------------------------------------ #

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
    def current(self):
        return self.__current

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

    def current_song_search(self):
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

    async def create_local_song_player(self, search_term: str):
        try:
            music = self.musics.search(search_term)
            if music is None:
                raise CustomError(EnumMessages.ERROR_NOT_FOUND)
            player = self.__voice.create_ffmpeg_player(music.filename, after=self.toggle_next)
            player.title = music.full_title
            player.artist = music.artists
            player.duration = music.duration
            player.search = music.name + " " + music.artists
            player.download_url = music.idt
            return player
        except Exception as e:
            error = "An error occurred while processing this request: ```py\n{}: {}\n```".format(type(e).__name__, e)
            LogManager().err.println(error)
            raise CustomError(EnumMessages.ERROR_NOT_FOUND)

    async def random_local_song_player(self):
        return await self.create_local_song_player(str(rnd.randint(1, self.musics.num_music)))

    async def create_ytdl_song_player(self, search_term: str):
        try:
            opts = {'default_search': 'auto', 'quiet': True}
            player = await self.__voice.create_ytdl_player(search_term, ytdl_options=opts, after=self.toggle_next)
            player.search = player.title
            return player
        except Exception as e:
            error = "An error occurred while processing this request: ```py\n{}: {}\n```".format(type(e).__name__, e)
            LogManager().err.println(error)
            raise CustomError(EnumMessages.ERROR_NOT_FOUND)

    async def __remake_player(self, player: discord.voice_client.StreamPlayer):

        if hasattr(player, 'yt'):
            return await self.create_ytdl_song_player(player.download_url)
        else:
            return await self.create_local_song_player(player.download_url)

    async def request_song(self, message: discord.Message, player: discord.voice_client.StreamPlayer):

        # Create a request
        if hasattr(player, 'yt'):
            entry = YTRequest(message, player)
        else:
            entry = LMRequest(message, player)

        # Playing a songs?
        if not self.songs.stopped() or self.is_playing():
            entry.enqueued_message = await self.bot.send_message(message.channel, embed=entry.message_enqueued())

        # Save the request
        LogManager().out.println("Song request - " + entry.player.title)
        await self.songs.add(entry)

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

        """ IS_PLAYING """
        if not self.is_playing():
            # Not playing any music right now
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_WTOUT_MS))
            return

        # Get skip author
        voter = message.author
        # Get author channel
        voter_channel: discord.Channel = message.author.voice_channel
        # Get bot channel
        bot_channel: discord.Channel = self.__voice.channel
        # skip needed
        skip_needed = max(1, np.ceil(len(bot_channel.voice_members) / 2.0))

        """ SAME_CHANNEL """
        if voter_channel != bot_channel:
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_SAME_CHL))
            return

        await self.__skip_lock.acquire()

        if voter == self.__current.message.author:
            """ Requester requested skipping song """
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_REQ_SKIP))
            self.skip()

        elif voter.id not in self.skip_votes:
            """ You have not voted yet """
            self.skip_votes.add(voter.id)
            total_votes = len(self.skip_votes)

            if total_votes >= skip_needed:
                # Skip vote passed, skipping song
                await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_VOT_SKIP))
                self.skip()
            else:
                # Needs more vote
                await self.bot.say(embed=MessageBuilder.create_simple_info(
                    EnumMessages.CONTENT_SKIP_VOT_WAIT.format(total_votes, skip_needed)))

        else:
            """ You have already voted to skip this song """
            await self.bot.say(embed=MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_ALRD_VOT))

        self.__skip_lock.release()

    async def fn_goto_queue(self, item_id):
        try:
            await self.songs.goto(item_id)
        except IndexError as e:
            await self.bot.say(embed=MessageBuilder.create_error("ID inválido!"))
            print(e)
        except RuntimeError as e:
            await self.bot.say(embed=MessageBuilder.create_error("Fila vazia!"))
            print(e)
        else:
            self.skip()

    async def fn_show_queue(self, page=1):
        if self.songs.size == 0:
            await self.bot.say(embed=MessageBuilder.create_error("Empty queue!"))
        else:
            await self.bot.say(embed=MessageBuilder.create_info("Queue:", self.songs.display(page=page)))

    # ================================================================================================================ #
    #   Audio Player behavior
    # ---------------------------------------------------------------------------------------------------------------- #

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def __prepare_autoplay(self):
        # Empty songs queue and autoplay active?
        if self.songs.stopped() and self.__autoplay is not None and not self.is_playing():
            # Request a random song
            print("AUTOPLAY!")
            player = await self.random_local_song_player()
            await self.request_song(self.__autoplay, player)

    async def __prepare_song(self) -> Request:
        # Empty songs queue and autoplay active?
        await self.__prepare_autoplay()

        current = None
        while current is None:
            print("Pegando música ...")
            print("Queue: \n" + str(self.songs))
            current = await self.songs.wait()  # type: Request
            if current.player.is_done():
                current.player = await self.__remake_player(current.player)
            print("Liberado!")

        # check if exists and delete "enqueued" message
        if current.enqueued_message is not None:
            await self.bot.delete_message(current.enqueued_message)

        # delete request message (it will disable go back queue function)
        # if self.__autoplay is None or self.__autoplay.id != current.message.id:
        #    await self.bot.delete_message(current.message)

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
                except Exception as e:
                    pass
            except asyncio.CancelledError as e:
                return
            except Exception as e:
                print("Error in VoiceState 'audio_player_task' thread: ```py\n{}: {}\n```".format(type(e).__name__, e))
                self.__autoplay = None

# ================================================================================================================ #
