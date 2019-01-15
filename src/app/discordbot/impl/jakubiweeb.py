import discord
from discord.ext import commands

from ..enums import *
from ..utils import *
from ...config import Config
from ...localmusic import LocalMusicController

from .music import MusicApplication


class JakubiweebApplication(MusicApplication):

    def __init__(self, config: Config, musics: LocalMusicController):
        """
        JakubiWeeb application
        """
        super().__init__(config, musics)

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
        player = await state.voice.fn_request_local_song(ctx.message, song)


    # ================================================================================================================ #
    #   Command song lyrics search
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['lyrics', 'ly'])
    async def wlyrics(self, ctx: commands.Context, *args):

        from random import choice
        from ..utils.lyrics import AnimeLyrics
        from math import ceil

        song = ' '.join(args).strip()

        if len(song) <= 0:
            if self.states.get(ctx.message.server).voice.is_playing():
                song = self.states.get(ctx.message.server).voice.current_song().strip()
        else:
            song = ' '.join(args)

        try:
            result = AnimeLyrics(song)
        except Exception as e:
            print('Exceção na pesquisa de letras: '+str(e))
            await self.bot.send_message(ctx.message.channel, embed=MessageBuilder.create_error('Erro na pesquisa de letra para a música '+self.search_term))
            return

        song_text = result.lyrics
        n_msgs = ceil(len(song_text)/1850)

        nomes = ['weeb', 'otaku', 'lolicon', 'ancap', 'woof', 'rebounce', 'rabetão', 'peixe']
        adjetivos = ['safado', 'kawaii', 'ancapistão', 'de boas', 'palone', 'tbdc', 'estadista']

        embed = discord.Embed(title='Ta aí, seu {} {}'.format(choice(nomes),choice(adjetivos)), color=0x46ff42)
        await self.bot.send_message(ctx.message.channel, embed=embed)

        if n_msgs == 1:
            await self.bot.send_message(ctx.message.channel, content='```{}```'.format(song_text))
        else:
            lines = song_text.split('\n')
            descriptions = [0 for i in range(n_msgs)]

            counter = 0
            n = 0
            k = 1

            while n < len(lines):
                counter += len(lines[n])
                if counter > k * 1850:
                    counter -= len(lines[n])
                    descriptions[k - 1] = '\n'.join(lines[:n])
                    del lines[:n]
                    n = 0
                    k += 1
                if k == n_msgs:
                    descriptions[n_msgs - 1] = '\n'.join(lines[:])
                    break

            for i in range(n_msgs):
                await self.bot.send_message(ctx.message.channel, content='```{}```'.format(descriptions[i]))

    # ================================================================================================================ #
    #   Queue functions
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['queue'])
    async def wqueue(self, ctx: commands.Context):
        state = self.states.get(ctx.message.server)

        embed = discord.Embed(title='Fila de músicas', color=0x5179d9)

        string = ''
        for index, music in enumerate(state.voice.queue.get_queue()):
            embed.add_field(name='[{}]'.format(str(index+1)), value=music, inline=False)
        await self.bot.send_message(ctx.message.channel, embed=embed)










