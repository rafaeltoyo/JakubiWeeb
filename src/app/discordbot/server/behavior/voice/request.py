import abc
import discord


class Request(abc.ABC):

    def __init__(self,
                 message: discord.Message,
                 player: discord.voice_client.StreamPlayer):
        self.message = message
        self.player = player
        self.enqueued_message = None

    def __str__(self):
        fmt = '*{0.title}* requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.message.author)

    @abc.abstractmethod
    def _title(self) -> str:
        raise Exception

    def __message_base(self, title, color):
        m = discord.Embed(
            title=title,
            description=self._title(),
            color=color
        )
        if self.message:
            m.set_author(
                name="Requested by: " + self.message.author.nick,
                icon_url=self.message.author.avatar_url
            )
        if hasattr(self.player, 'duration') and self.player.duration:
            d_min, d_seg = divmod(self.player.duration, 60)
            m.add_field(name="Duration:", value='{0[0]}m {0[1]}s'.format((str(int(d_min)), str(int(d_seg)))))
        return m

    def message_playing(self):
        m = self.__message_base("Now playing", discord.Color.dark_green())
        return m

    def message_enqueued(self):
        m = self.__message_base("Enqueued", discord.Color.dark_blue())
        return m

    def message_now_playing(self):
        m = self.message_playing()
        return m


class YTRequest(Request):

    def __init__(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        super().__init__(message, player)

    def _title(self) -> str:
        return '*{0.title}* uploaded by {0.uploader}'.format(self.player)


class LMRequest(Request):

    def __init__(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        super().__init__(message, player)

    def _title(self) -> str:
        return '*{0.title}* by {0.artist}'.format(self.player)
