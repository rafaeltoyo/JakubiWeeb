from localmusic import *

from .config import *


class Bot:

    def __init__(self, *args, **kwargs):

        # Configuration
        self.config = Config()

        # Local music controller
        self.__music = LocalMusicController()

        self.__start()

    def __del__(self):
        del self.config
        del self.__music

    def __start(self, *args, **kwargs):

        try:
            # Load configuration file
            self.config.load()

        except Exception as e:
            print("Unable to start the bot!")
            raise e

    def run(self, *args, **kwargs):

        print(self.__music.search(2))
        print(self.__music.search("Yell"))
        print('\n'.join([str(i) for i in self.__music.search_all("Yell")]))

    def load_music(self):

        self.__music.load(path=self.config.params.music_folder)
