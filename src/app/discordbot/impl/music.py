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
    def lyrics_search(self) -> LyricsSearchManager:
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

        if state.voice.is_playing():
            await self.bot.say(embed=state.voice.current.message_playing())
        else:
            await self.bot.say(embed=MessageBuilder.create_alert(EnumMessages.ERROR_NOT_PLAYING))

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
    #   Command queue
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['q'])
    async def queue(self, ctx: commands.Context, *args):
        """
        Display current queue.
        $queue OR $queue [page:int]
        """
        state = self.states.get(ctx.message.server)

        if len(args) == 0:
            await state.voice.fn_show_queue(page=1)
        elif len(args) == 1:
            try:
                page = int(args[0])
            except:
                await self.bot.say(embed=MessageBuilder.create_error("Tem coisa errada ai filhão!"))
            else:
                await state.voice.fn_show_queue(page=page)
        else:
            await self.bot.say(embed=MessageBuilder.create_error("Tem coisa demais ai filhão!"))

    # ================================================================================================================ #
    #   Command remove
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['r', 'rem', 'remv', 'delete', 'del'])
    async def remove(self, ctx: commands.Context, song_id: int):
        """
        Go to specific song in queue
        """
        state = self.states.get(ctx.message.server)
        try:
            item = await state.voice.songs.remove(song_id)
        except IndexError as e:
            await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.ERROR_NOT_FOUND))
            print(e)
        except RuntimeError as e:
            await self.bot.say(embed=MessageBuilder.create_error("Fila vazia!"))
            print(e)
        else:
            if state.voice.is_playing() and state.voice.current == item:
                print(state.voice.current.player.title)
                print(item.player.title)
                state.voice.skip()
            if item is not None:
                del item

    # ================================================================================================================ #
    #   Command goto
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['goto', 'jump'])
    async def jumpto(self, ctx: commands.Context, song_id: int):
        """
        Go to specific song in queue
        """
        state = self.states.get(ctx.message.server)
        try:
            await state.voice.songs.goto(song_id)
        except IndexError as e:
            await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.ERROR_NOT_FOUND))
            print(e)
        except RuntimeError as e:
            await self.bot.say(embed=MessageBuilder.create_error("Fila vazia!"))
            print(e)
        else:
            state.voice.skip()

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

        try:
            player = await state.voice.create_ytdl_song_player(song)
            await state.voice.request_song(ctx.message, player)
        except Exception as e:
            await self.bot.say(embed=MessageBuilder.create_error(str(e)))

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
                search_term = state.voice.current_song_search().strip()
            else:
                await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.LYRICS_SEARCH_INVALID))
                return

        from random import choice
        nomes = ['weeb', 'otaku', 'lolicon', 'ancap', 'woof', 'rebounce', 'rabetão', 'peixe']
        adjetivos = ['safado', 'kawaii', 'ancapistão', 'de boas', 'palone', 'tbdc', 'estadista']
        content = "Ta aí, seu {} {}.".format(choice(nomes), choice(adjetivos))

        try:
            # Google search
            lyrics = self.lyrics_search.search(search_term)
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
