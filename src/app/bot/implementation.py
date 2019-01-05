import discord
from discord.ext import commands

from .behavior.interface import CommandsInterface
from .behavior import *
from .enums import *
from .utils import *


class JakubiWeeb(CommandsInterface):

    def __init__(self, app):
        """
        JakubiWeeb implementation
        :param app: Application instance
        """
        super().__init__(app)

        self.states = VoiceStateController(self.bot)

    # ================================================================================================================ #
    #   Command summon
    # ---------------------------------------------------------------------------------------------------------------- #

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx: commands.Context):
        """Summons the bot to join your voice channel."""

        # Get Author Channel
        summoned_channel = ctx.message.author.voice_channel  # type: discord.Channel

        if summoned_channel is None:
            # Author aren't in a voice channel
            await self.bot.say(embed=MessageBuilder.create_error(EnumMessages.ERROR_1))
        else:
            # Get server voice state
            vstate = self.states.get_voice_state(ctx.message.server)

            if vstate.voice is None:
                # Join in channel
                vstate.voice = await self.bot.join_voice_channel(summoned_channel)
            else:
                # Move to channel
                await vstate.voice.move_to(summoned_channel)

    # ================================================================================================================ #
    #   Command playing
    # ---------------------------------------------------------------------------------------------------------------- #

    async def __playing(self, ctx: commands.Context):
        vstate = self.states.get_voice_state(ctx.message.server)

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx: commands.Context):
        await self.__playing(ctx)

    @commands.command(pass_context=True, no_pm=True)
    async def np(self, ctx: commands.Context):
        await self.__playing(ctx)

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
    #   Autoplay
    # ---------------------------------------------------------------------------------------------------------------- #

    # ================================================================================================================ #
