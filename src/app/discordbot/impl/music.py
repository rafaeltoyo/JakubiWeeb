from discord.ext import commands

from ..enums import *
from ..utils import *
from .voice import BaseVoiceApplication
from app.lyrics.genius import GeniusAPI


class MusicApplication(BaseVoiceApplication):

    # ================================================================================================================ #
    #   Command playing
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['np', 'now', 'current'])
    async def playing(self, ctx: commands.Context):
        """
        Shows info about the currently played song.
        """
        state = self.states.get(ctx.message.server)
        await state.voice.fn_now_playing()

    # ================================================================================================================ #
    #   Command skip
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['skp'])
    async def skip(self, ctx: commands.Context):
        """
        Vote to skip a song.
        The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        state = self.states.get(ctx.message.server)
        await state.voice.fn_skip_song(ctx.message)

    # ================================================================================================================ #
    #   Command resume
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['rsm'])
    async def resume(self, ctx: commands.Context):
        """
        Resumes the currently played song.
        """
        state = self.states.get(ctx.message.server)
        state.voice.resume()

    # ================================================================================================================ #
    #   Command pause
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx: commands.Context):
        """
        Pauses the currently played song.
        """
        state = self.states.get(ctx.message.server)
        state.voice.pause()

    # ================================================================================================================ #
    #   Command volume
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['v'])
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Vote to skip a song.
        The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        state = self.states.get(ctx.message.server)
        await state.voice.volume(float(volume / 100.0))

    # ================================================================================================================ #
    #   Command play
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['p', 'plei'])
    async def play(self, ctx: commands.Context, *, song: str):
        """
        Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.states.get(ctx.message.server)

        if not state.voice.is_connected():
            success = await ctx.invoke(self.summon)
            if not success:
                return
        await state.voice.fn_request_yt_song(ctx.message, song)