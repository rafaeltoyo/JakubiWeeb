import os
import re

from model.music import Music
from model.anime import Anime


class FileLoader(object):

    def __init__(self, path=""):
        self.path = path

    def __explore(self, path: str, ext: str = "", deep: bool = False):
        # Get all folders from path
        pieces = [p for p in path.replace('/', '\\').split('\\') if p is not None and len(str(p)) > 0]
        if pieces[0].rfind('/[A-Z]:/') and os.name == "nt":
            # Absolute path in windows
            pieces[0] = pieces[0] + os.sep
        # Rebuild the path
        path = os.path.join(*pieces)

        # For all items in dir ...
        for item in os.listdir(path):

            itempath = path + os.sep + item

            if ext == "dir":
                if os.path.isdir(itempath):
                    yield (item, itempath)
                else:
                    continue

            # 'deep' == True => Recursive search
            if deep and os.path.isdir(itempath):
                for p in self.__explore(path=itempath, ext=ext, deep=deep):
                    yield p
            else:
                if ext is None or ext == "" or ext == "all":
                    yield (item, itempath)
                elif ext.startswith('.') and item.endswith(ext) or item.endswith('.' + ext):
                    yield (item.replace(ext, ''), itempath)

    def search_mp3(self):
        """
        Example: MP3 search
        :return:
        """
        return (p for p in self.__explore(path=self.path, ext=".mp3", deep=True))

    def search_animes(self):
        """
        Anime search
        :return:
        """
        animes = []
        for data in self.__explore(path=self.path, ext="dir", deep=False):
            anime = Anime(*data)

            match = re.search('^(- |@ )(.*)', anime.name)
            print(match.group(2) if match is not None else "")
            if match is not None and len(match.group(2)) > 0:
                anime.name = match.group(2)

            for (music, folder) in self.__explore(path=anime.folder, ext=".mp3", deep=True):
                anime.append(Music(music, folder))
            animes.append(anime)
            yield anime
