import os
import re

from model.music import Music
from model.anime import Anime


class FileLoader(object):

    def __init__(self, path=""):
        self.path = path

    def __explore(self, path: str, ext: str = "", deep: bool = False):
        """
        Explore path.
        :param path: Path to explore.
        :param ext: Requested extension.
                    "" or "all" will return all files and folders.
                    "dir" will return all folders.
                    "files" will return all files.
                    ".xxx" will return all ".xxx" files.
                    ".xxx|.yyy" will return all ".xxx" or ".yyy" files.
        :param deep: Recursive search (Only works with file search).
        :return:
        """
        # Get all folders from path
        pieces = [p for p in path.replace('/', '\\').split('\\') if p is not None and len(str(p)) > 0]
        if pieces[0].rfind('/[A-Z]:/') and os.name == "nt":
            # Absolute path in windows
            pieces[0] = pieces[0] + os.sep
        # Rebuild the path
        path = os.path.join(*pieces)

        """ Parse ext command """
        onlydir_mode = ext is not None and ext in ["dir", "folder"]
        filter_mode = not onlydir_mode or not (ext is None or ext in ["", "all", "complete"])

        extensions = [(('.' if not i.startswith('.') else '') + i) for i in ext.split('|')] if filter_mode else []

        # ============================================================================================================ #

        for filename in os.listdir(path):
            # Build completed filename
            filename_path = path + os.sep + filename

            """ FOLDER request """
            if onlydir_mode:
                if os.path.isdir(filename_path):
                    yield (filename, filename_path)
                else:
                    continue

            """ FILE request with recursive search """
            if deep and os.path.isdir(filename_path):
                for p in self.__explore(path=filename_path, ext=ext, deep=deep):
                    yield p
                continue

            """ FILE/FOLDER request """
            if filter_mode:
                # Files that ends with requested extension
                for extension in extensions:
                    if filename.endswith(extension):
                        yield (filename.replace(extension, ''), filename_path)
            else:
                # All files/folders
                yield (filename, filename_path)

    def search_mp3(self):
        """
        Example: MP3 search
        :return:
        """
        return (p for p in self.__explore(path=self.path, ext=".mp3", deep=True))

    def search_file(self, ext=".mp3"):
        """
        Example: file search
        :return:
        """
        return (p for p in self.__explore(path=self.path, ext=ext, deep=True))

    def search_animes(self):
        """
        Anime search (Custom function to read my music folder).
        :return:
        """
        # Search directories in my music folder.
        for data in self.__explore(path=self.path, ext="dir", deep=False):
            # Save the folder name as anime name and the folder path
            anime = Anime(*data)

            # Check incomplete folder prefix
            match = re.search('^(- |@ )(.*)', anime.name)

            if match is not None and len(match.group(2)) > 0:
                # Fix anime name
                anime.name = match.group(2)

            # Search mp3 files into anime folder.
            for (music, folder) in self.__explore(path=anime.folder, ext=".mp3", deep=True):
                anime.append(Music(music, folder))

            yield anime  # Return the anime
