from discord.ext import commands

from ..enums import *
from ..utils import *
from .voice import BaseVoiceApplication
from ...config import Config
from ...localmusic import LocalMusicController
from ...lyrics.urlparse.manager import LyricsSearchManager
from ...lyrics.api.genius import GeniusAPI


class MusicApplication(BaseVoiceApplication):

    def __init__(self, config: Config, musics: LocalMusicController, lyrics: LyricsSearchManager):
        super().__init__(config, musics)
        self.__lyrics = lyrics

    @property
    def lyrics(self) -> LyricsSearchManager:
        return self.__lyrics

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

    # ================================================================================================================ #
    #   Command lyrics
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['ly'])
    async def lyrics(self, ctx: commands.Context, *args):
        """
        Current song lyrics
        """
        state = self.states.get(ctx.message.server)

        # Create search parameter
        search_term = " ".join(args).strip()
        if len(search_term) <= 0:
            if state.voice.is_playing():
                search_term = state.voice.current_song().strip()
            else:
                await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.LYRICS_SEARCH_INVALID))
                return

        from random import choice
        nomes = ['weeb', 'otaku', 'lolicon', 'ancap', 'woof', 'rebounce', 'rabetão', 'peixe']
        adjetivos = ['safado', 'kawaii', 'ancapistão', 'de boas', 'palone', 'tbdc', 'estadista']
        content = "Ta aí, seu {} {}.".format(choice(nomes), choice(adjetivos))

        try:
            # Google search
            lyrics = self.lyrics.search(search_term)
            # Invoke API
            # lyrics = GeniusAPI(self.config.params.genius_apikey).get_lyrics(search_term)
        except Exception as e:
            print('Exceção na pesquisa de letras: ' + str(e))
            lyrics = None

        # Lyrics return handler
        if lyrics is not None and len(lyrics.content) > 0:
            await self.bot.say(embed=MessageBuilder.create_info(
                content + " " + EnumMessages.LYRICS_SEARCH_RESULT,
                "Link: {}".format(lyrics.source)))
            output = ""
            for i in lyrics.content.split("\n"):
                if len(output) + len(i) > 1994:
                    await self.bot.say("```{}```".format(output))
                    output = ""
                output += i + "\n"
            if len(output.replace("\n", "")) > 0:
                await self.bot.say("```{}```".format(output))
        else:
            await self.bot.say(
                embed=MessageBuilder.create_error(EnumMessages.LYRICS_SEARCH_NOT_FOUND.format(search_term)))

# ==================================================================================================================== #
