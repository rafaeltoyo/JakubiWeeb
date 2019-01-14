import discord

from ..enums import EnumMessages


class MessageBuilder:

    @staticmethod
    def create_base_message(title: str, content: str, color: discord.Color):
        return discord.Embed(
            title=title,
            description=content,
            color=color)

    @staticmethod
    def create_alert(content: str):
        return MessageBuilder.create_base_message(
            title=EnumMessages.TITLE_ALERT,
            content=content,
            color=discord.Color.dark_gold())

    @staticmethod
    def create_error(content: str):
        return MessageBuilder.create_base_message(
            title=EnumMessages.TITLE_ERROR,
            content=content,
            color=discord.Color.dark_red())

    @staticmethod
    def create_info(title: str, content: str):
        return discord.Embed(
            title=title,
            content=content,
            color=discord.Color.dark_blue())

    @staticmethod
    def create_simple_info(content: str):
        return discord.Embed(
            description=content,
            color=discord.Color.dark_blue())