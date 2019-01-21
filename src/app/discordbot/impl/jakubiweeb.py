import discord
from discord.ext import commands

from ..enums import *
from ..utils import *
from ...config import Config
from ...localmusic import LocalMusicController
from ...lyrics.urlparse.manager import LyricsSearchManager

from .music import MusicApplication


class JakubiweebApplication(MusicApplication):

    def __init__(self, config: Config, musics: LocalMusicController, lyrics: LyricsSearchManager):
        """
        JakubiWeeb application
        """
        super().__init__(config, musics, lyrics)

    # ================================================================================================================ #
    #   Command local song autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['wap', 'autoplay', 'ap', 'weebparty'])
    async def wautoplay(self, ctx: commands.Context):
        """
        Autoplay weeb songs.
        """
        state = self.states.get(ctx.message.server)

        if not state.voice.is_connected():
            success = await ctx.invoke(self.summon)
            if not success:
                return
        await state.voice.fn_autoplay(ctx.message)

    # ================================================================================================================ #
    #   Command local song search
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['search', 'weebs'])
    async def wsearch(self, ctx: commands.Context, *, song: str):
        """
        Search a weeb song.
        """
        content = ""
        try:
            for music in self.musics.search_all(song, num=20):
                title = "[{0.idt}] **{0.name}** by __{0.artists}__ [{1}]".format(music, music.formatted_duration())
                title = title[0:69] if len(title) > 70 else title
                info = "*{0.title}* ".format(music, )
                content += title + "\n\t" + info + "\n"

        except Exception as e:
            content = ""
            print('Erro na consulta (wsearch)!' + str(e))

        finally:
            if len(content) <= 0:
                msg = MessageBuilder.create_error(EnumMessages.CONTENT_SEARCH_NOT_FOUND)

            else:
                msg = discord.Embed(
                    title=EnumMessages.TITLE_SEARCH_RESULT,
                    description=content,
                    color=discord.Color.dark_gold())
                msg.add_field(
                    name=EnumMessages.CONTENT_SEARCH_RESULT_TTL_FLD,
                    value=str(self.musics.num_folder), inline=True)
                msg.add_field(
                    name=EnumMessages.CONTENT_SEARCH_RESULT_TTL_MSC,
                    value=str(self.musics.num_music), inline=True)

            await self.bot.send_message(ctx.message.channel, embed=msg)

    # ================================================================================================================ #
    #   Command local song play
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['wp', 'weeb'])
    async def wplay(self, ctx: commands.Context, *, song: str):
        """
        Plays a local song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches in sqlite3 database and load the music file.
        """
        state = self.states.get(ctx.message.server)

        if not state.voice.is_connected():
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_local_song_player(song)
            await state.voice.request_song(ctx.message, player)
        except Exception as e:
            await self.bot.say(embed=MessageBuilder.create_error(str(e)))

    # ================================================================================================================ #
