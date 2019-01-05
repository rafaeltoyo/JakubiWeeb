from localmusic import *

from .config import *
from .bot import *


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
        self.music = LocalMusicController()

        self.__start(*args)

    def __del__(self):
        del self.config
        del self.music

    # ================================================================================================================ #
    #   Start
    # ---------------------------------------------------------------------------------------------------------------- #

    def __start(self, *args):

        try:
            # Load configuration file
            self.config.load()

            # Load database tables
            self.music.init_db()

            # self.music.load(path=self.config.params.music_folder)

        except Exception as e:
            print("Unable to start the bot!")
            raise e

    # ================================================================================================================ #
    #   Run
    # ---------------------------------------------------------------------------------------------------------------- #

    def run(self):
        JakubiWeeb(self).run()

    # ================================================================================================================ #
