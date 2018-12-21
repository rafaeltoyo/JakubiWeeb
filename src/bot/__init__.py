import re
import asyncio
import discord
from discord.ext import commands
from mutagen.mp3 import MP3

from .voicechannel import VoiceStateFactory, VoiceState
from model.music import Music

from utils.config import Config
from utils.db import Database


# ==================================================================================================================== #


class Jakubiweeb:

    def __init__(self, bot: commands.Bot, cf: Config, db: Database):
        self.bot = bot
        self.factory = VoiceStateFactory(bot)
        self.cf = cf
        self.db = db

    def __unload(self):
        self.factory.unload()

    # ---------------------------------------------------------------------------------------------------------------- #

    def __error_msg(self, description: str):
        return discord.Embed(
            title='Error!',
            description=description,
            color=discord.Color.red())

    def __default_msg(self, title: str, description: str):
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.dark_blue())

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def tbdc(self, ctx: commands.Context):
        """THIAGO BISPO DÁ O CU!"""
        emoji = None
        for emoji in ctx.message.server.emojis:
            if emoji.name == "Butterpride":
                break
        await self.bot.add_reaction(ctx.message, emoji)
        await self.bot.say(embed=self.__default_msg("Thiago Bispo dá o cu!", "Bem entendido isso? :Butterpride:"))

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx: commands.Context):
        """Summons the bot to join your voice channel."""

        # Get Author Channel
        summoned_channel = ctx.message.author.voice_channel  # type: discord.Channel
        if summoned_channel is None:
            await self.bot.say(embed=self.__error_msg('You are not in a voice channel.'))
            return False

        # Get Bot Channel
        state = self.factory.get_voice_state(ctx.message.server)

        if state.voice is None:
            # Join in channel
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            # Move to channel
            await state.voice.move_to(summoned_channel)

        return True

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx: commands.Context, value: int):
        """Sets the volume of the currently playing song."""

        if 0 > value > 100:
            await self.bot.say(embed=self.__error_msg('Invalid volume. Only values ​​between 0 and 100'))

        state = self.factory.get_voice_state(ctx.message.server)
        state.volume = value / 100

        if state.is_playing():
            state.player.volume = state.volume

        await self.bot.say('`Set the volume to {:.0%}`'.format(state.volume))

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx: commands.Context, *, song: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.factory.get_voice_state(ctx.message.server)
        opts = {'default_search': 'auto', 'quiet': True}

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            await state.request_song(ctx.message, player)

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def wplay(self, ctx: commands.Context, *, song: str):
        """Plays a weeb song. $wplay [search] OR $wplay [song ID]"""
        state = self.factory.get_voice_state(ctx.message.server)

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        music_data = []

        if re.search('^[0-9]+$', song):
            # SEARCH SONG BY ID
            cursor = self.db.conn.cursor()
            cursor.execute("""
                            SELECT * FROM anime_music 
                            WHERE folder LIKE (
                                SELECT filename FROM music WHERE music.id = (?)
                            )""", (int(song),))
            music_data = cursor.fetchone()
            cursor.close()
        else:
            # SEARCH SONG BY NAME
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT * FROM anime_music 
                WHERE anime_music MATCH (?) 
                ORDER BY rank""", (song,))
            music_data = cursor.fetchone()
            cursor.close()

        if music_data is None or len(music_data) <= 0:
            await self.bot.send_message(ctx.message.channel, embed=self.__error_msg("Não achei sa coisa não, woof!"))
            return

        try:
            mp3 = MP3(music_data[4])
            player = state.voice.create_ffmpeg_player(music_data[4], after=state.toggle_next)
            player.title = music_data[2] + ' ({})'.format(music_data[1])
            player.artist = ' & '.join(music_data[3].split('/'))
            player.duration = mp3.info.length if mp3 else 0
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            await state.request_song(ctx.message, player)

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx: commands.Context):
        """Pauses the currently played song."""
        state = self.factory.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.factory.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx: commands.Context):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.factory.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.factory.voice_states[server.id]
            await self.bot.say('Adeus :(')
            await state.voice.disconnect()
        except:
            pass

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx: commands.Context):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.factory.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('`Not playing any music right now...`')
            return

        voter = ctx.message.author
        if voter == state.current.message.author:
            await self.bot.say('`Requester requested skipping song...`')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('`Skip vote passed, skipping song...`')
                state.skip()
            else:
                await self.bot.say('`Skip vote added, currently at [{}/3]`'.format(total_votes))
        else:
            await self.bot.say('`You have already voted to skip this song.`')

    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx: commands.Context):
        """Shows info about the currently played song."""

        state = self.factory.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('`Not playing anything.`')
        else:
            skip_count = len(state.skip_votes)
            embed = state.current.message_now_playing()
            embed.add_field(name="Skips:", value='[skips: {}/3]'.format(skip_count))
            await self.bot.say(embed=embed)

# ==================================================================================================================== #
