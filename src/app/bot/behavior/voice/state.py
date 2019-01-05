import asyncio
import random as rnd

import discord
from discord.ext import commands

from .request import Request, YTRequest, MP3Request
from ...implementation import JakubiWeeb
from ...enums import *
from ...utils import *


class VoiceState:

    def __init__(self, jw: JakubiWeeb):
        """
        Voice State:
        When the bot connect in some server, we create a state for this server.
        :param bot:
        """

        self.current = None  # type: Request
        self.voice = None  # type: discord.VoiceClient
        self.autoplay = None  # type: discord.Message
        self.volume = 0.3  # type: float

        # instance of the bot
        self.jw = jw
        self.bot = jw.bot

        # flag to access songs queue
        self.play_next_song = asyncio.Event()
        # songs queue
        self.songs = asyncio.Queue()

        # a set of user_ids that voted
        self.skip_votes = set()

        # thread: wait songs
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    @property
    def player(self):
        return self.current.player

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    async def toggle_autoplay(self, message: discord.Message):
        """
        Toggle the autoplay flag.
        :param message: Autoplay request
        :return: autoplay final value
        """
        # Lock autoplay flag
        with self.autoplay:

            if self.autoplay is None:
                # If None then autoplay is off
                # Save the message to known the requester
                self.autoplay = message

                if self.songs.empty() and not self.is_playing():
                    await self.request_random_local_song()
                return True
            else:
                # Else autoplay is on
                self.autoplay = None
                return False

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    # ================================================================================================================ #
    #   Request a music
    # ---------------------------------------------------------------------------------------------------------------- #

    async def request_yt_song(self, message: discord.Message, search: str):
        opts = {'default_search': 'auto', 'quiet': True}
        player = await self.voice.create_ytdl_player(search, ytdl_options=opts, after=self.toggle_next)
        await self.request_song(message, player)

    async def request_local_song(self, message: discord.Message, search: str):
        # Search
        music = self.jw.musics.search(search)
        if music is not None:
            player = self.voice.create_ffmpeg_player(music.filename, after=self.toggle_next)
            player.title = "[{0.id}] {0.name} ({0.title})".format(music)
            player.artist = music.artists
            player.duration = music.duration
            await self.request_song(message, player)
        else:
            raise Exception("Music not found!")

    async def request_random_local_song(self):
        if self.autoplay is None:
            return
        music_id = rnd.randint(1, self.jw.musics.num_music)
        await self.request_local_song(self.autoplay, str(music_id))

    async def request_song(self, message: discord.Message, player: discord.voice_client.StreamPlayer):

        # Create a request
        if hasattr(player, 'yt'):
            entry = YTRequest(message, player)
        else:
            entry = MP3Request(message, player)

        # Playing a songs?
        if not self.songs.empty() or self.is_playing():
            entry.enqueded_msg = await self.bot.send_message(message.channel, embed=entry.message_enqueued())

        # Save the request
        await self.songs.put(entry)

    # ================================================================================================================ #
    #   Is playing ?
    # ---------------------------------------------------------------------------------------------------------------- #

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        player = self.current.player
        return not player.is_done()

    def msg_playing(self):
        pass

    # ================================================================================================================ #
    #   Skip
    # ---------------------------------------------------------------------------------------------------------------- #

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    async def vote_skip(self, message: discord.Message):

        if not self.is_playing():
            # Not playing any music right now
            await self.bot.say(MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_WTOUT_MS))
            return

        # Skipping music
        # Get skip author
        voter = message.author

        if voter == self.current.message.author:
            # Requester requested skipping song
            await self.bot.say(MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_REQ_SKIP))
            self.skip()
        elif voter.id not in self.skip_votes:
            # You have not voted yet
            self.skip_votes.add(voter.id)
            total_votes = len(self.skip_votes)
            if total_votes >= 3:
                # Skip vote passed, skipping song
                await self.bot.say(MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_VOT_SKIP))
            else:
                # Needs more vote
                await self.bot.say(
                    MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_VOT_WAIT.format(total_votes)))
        else:
            # You have already voted to skip this song
            await self.bot.say(MessageBuilder.create_simple_info(EnumMessages.CONTENT_SKIP_ALRD_VOT))

    # ================================================================================================================ #
    #   Thread: audio player task
    # ---------------------------------------------------------------------------------------------------------------- #

    async def audio_player_task(self):
        while True:
            try:
                """ Starting the loop """

                # CLEAR next song flag
                self.play_next_song.clear()

                """ Autoplay validation """

                # Get next song or wait
                if self.songs.empty() and self.autoplay is not None:
                    # If empty song queue and autoplay is on then put a random song in queue
                    await self.request_random_local_song()

                """ Get the next song (wait if necessary) """

                self.current = await self.songs.get()  # type: Request

                # check if exists and delete "enqueued" message
                if self.current.enqueued_message is not None:
                    await self.bot.delete_message(self.current.enqueued_message)

                """ Play current song """

                # build "playing" message
                embed = self.current.message_playing()
                msg = await self.bot.send_message(self.current.message.channel, embed=embed)  # type: discord.Message

                # delete request message
                if self.autoplay is None or self.autoplay.id != self.current.message.id:
                    await self.bot.delete_message(self.current.message)

                # set user volume
                self.current.player.volume = self.volume
                # start music
                self.current.player.start()

                """ Wait for song end """

                # WAIT next song flag (skip or end)
                await self.play_next_song.wait()
                # delete "playing" message
                await self.bot.delete_message(msg)

            except Exception as e:
                print("Error in VoiceState 'audio_player_task' thread: \n" + str(e))
                self.autoplay = None

    # ================================================================================================================ #
