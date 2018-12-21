import abc
import discord


class Request:

    def __init__(self,
                 message: discord.Message,
                 player: discord.voice_client.StreamPlayer):
        self.message = message
        self.player = player
        self.enqueued_message = None

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.message.author)

    @abc.abstractmethod
    def __title(self) -> str:
        pass

    def __full_title(self):
        return self.__title

    def get_embeded_msg(self):
        m = discord.Embed(
            title='Now playing:',
            description=self.__title(),
            color=discord.Color.dark_green()
        )
        if self.message:
            m.add_field(name="Requested by:", value=self.message.author.display_name, inline=True)
        if self.player.duration:
            m.add_field(name="Duration:", value='{0[0]}m {0[1]}s'.format(divmod(self.player.duration, 60)), inline=True)
        return m


class YTRequest(Request):

    def __init__(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        super().__init__(message, player)

    def __title(self) -> str:
        return '*{0.title}* uploaded by {0.uploader}'.format(self.player)


class MP3Request(Request):

    def __init__(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        super().__init__(message, player)

    def __title(self) -> str:
        return '*{0.title}* by {0.artist}'.format(self.player)
