import discord
from discord.ext import commands

from ..enums import *
from ..utils import *

from .base import DiscordApplication


class BaseVoiceApplication(DiscordApplication):

    # ================================================================================================================ #
    #   Command summon
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['vem', 'invoke', 'smmn'])
    async def summon(self, ctx: commands.Context):
        """
        Summons the bot to join your voice channel.
        """

        # Get Author Channel
        summoned_channel = ctx.message.author.voice_channel  # type: discord.Channel

        if summoned_channel is None:
            # Author aren't in a voice channel
            await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.ERROR_1))
            return False
        else:
            # Get server voice state
            state = self.states.get(ctx.message.server)
            await state.summon(summoned_channel)
            return True

    # ================================================================================================================ #
    #   Command stop
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True, aliases=['bye', 'die'])
    async def stop(self, ctx: commands.Context):
        """
        Vote to skip a song.
        The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        state = self.states.get(ctx.message.server)

        try:
            await state.voice.disconnect()
            await self.bot.say('Megôooooons!')
        except:
            pass

    # ================================================================================================================ #
