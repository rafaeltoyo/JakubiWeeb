from typing import List

from .loader import LocalMusicLoader
from .model import Music

import utils.singleton as singleton


class LocalMusicController(metaclass=singleton.Singleton):
    EXTENSION = [".mp3", ".m4a", ".mp4", ".flac"]

    def __init__(self):
        self.music = []  # type: List[Music]

    def load(self, path="", n_threads=0):

        for item in LocalMusicLoader().load(path):
            print(item)
            print(item.title)
