from typing import List, Any

from model.music import Music


class Anime(object):
    name: str
    folder: str
    __musics: List[Music]

    def __init__(self, name: str = "", folder: str = ""):
        self.name = name
        self.folder = folder
        self.__musics = []

    def append(self, music: Music):
        self.__musics.append(music)

    def __iter__(self):
        return (m for m in self.__musics)

    def __str__(self):
        header = "Anime: <%s>" % self.name
        content = ''.join(["%s \n" % str(p) for p in self.__musics])
        return header + '\n' + content
