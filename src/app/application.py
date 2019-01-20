from .discordbot import JakubiweebApplication

from .config import Config
from .localmusic import LocalMusicController
from .lyrics import LyricsSearchManager, AnimeLyrics, LetrasMus, Smule

from utils.log.manager import LogManager


class Application:

    # ================================================================================================================ #

    def __init__(self, *args):
        """
        Main application controller
        :param args: Command line parameters
        """
        # Configuration
        self.config = Config()

        # Local music controller
        self.musics = LocalMusicController()

        # Lyrics search service
        self.lyrics = LyricsSearchManager()
        self.lyrics.add(AnimeLyrics())
        self.lyrics.add(LetrasMus())
        self.lyrics.add(Smule())

        self.__start(*args)

    def __del__(self):
        del self.config
        del self.musics
        del self.lyrics

    # ================================================================================================================ #
    #   Start
    # ---------------------------------------------------------------------------------------------------------------- #

    def __start(self, *args):

        try:
            # Load configuration file
            self.config.load()

            # Load database tables
            self.musics.init_db()

        except Exception as e:
            print("Unable to start the bot!")
            raise e

    # ================================================================================================================ #
    #   Run
    # ---------------------------------------------------------------------------------------------------------------- #

    def run(self):
        # Reload local musics
        # self.musics.load(path=self.config.params.music_folder)

        # Create and launch a discord application
        app = JakubiweebApplication(self.config, self.musics, self.lyrics)
        app.run()

    # ================================================================================================================ #
