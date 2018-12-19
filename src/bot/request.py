import discord


class Request:

    def __init__(self, message: discord.Message, player: discord.voice_client.StreamPlayer):
        self.message = message
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
            return fmt.format(self.player, self.message.author)
