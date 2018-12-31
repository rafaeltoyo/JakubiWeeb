from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from .model import Music

import utils.singleton as singleton


class LMInvalidExtension(Exception):
    pass


class LocalMusicLoader(metaclass=singleton.Singleton):

    def __init__(self):
        """
        Local music loader.
        """
        # Valid extensions
        self.extension = LocalMusicLoader.Extensions(["mp3", "mp4", "m4a", "flac"])

    def _validate(self, path: Path):
        """
        Auxiliary method to validate file extension.
        :param path: Path object with filename
        :return: Path validated
        """
        if path.suffix not in self.extension:
            msg = "Invalid extension! \"{0.suffix}\" not in [{1}].".format(path, ", ".join(self.extension))
            raise LMInvalidExtension(msg)
        return path

    def _extract(self, path: Path):
        """
        Extract meta-data from music file like name and artists.
        This method uses mutagen lib to open the file.
        :param path: Path object with filename
        :return: List with meta-data
        """
        file = None
        title_tag = ""
        artist_tag = ""

        if path.suffix == '.mp3':
            # MP3 File
            file = MP3(path)
            title_tag = "TIT2"
            artist_tag = "TPE1"

        elif path.suffix in ['.m4a', '.mp4']:
            # MPEG4 File
            file = MP4(path)
            title_tag = chr(169) + "nam"
            artist_tag = chr(169) + "ART"

        elif path.suffix == '.flac':
            # FLAC File
            file = FLAC(path)
            title_tag = "title"
            artist_tag = "artists"

        if file is None or title_tag not in file.keys() or artist_tag not in file.keys():
            return ['', '']

        title = file.get(title_tag)
        artist = file.get(artist_tag)
        fixed_title = (str(title[0] if len(title) > 0 else "")) if isinstance(title, list) else str(title)
        fixed_artist = "/".join(artist) if isinstance(artist, list) else str(artist)

        return fixed_title, fixed_artist

    def _load_music(self, filename):
        """
        Load and extract info from music file.
        :param filename: Music filename (relative or absolute path).
        :return: Music info object
        """

        """ Load filename and validate extension """
        path = self._validate(filename if isinstance(filename, Path) else Path(str(filename)))
        info = Music(title=path.stem, filename=str(path.absolute()))

        """ Extract info """
        name, artists = self._extract(path)
        info.name = name
        info.artists = artists.replace("/", " & ")

        return info

    def load(self, path):
        """
        Load and extract info from music folder or files.
        :param filename: Music folder path or music filename (relative or absolute path).
        :return: Music info object (iterable)
        """
        path = path if isinstance(path, Path) else Path(str(path))
        if path.is_dir():
            for item in path.iterdir():
                try:
                    m = self._load_music(item)
                    yield m
                except LMInvalidExtension:
                    pass
        else:
            yield self._load_music(path)

    class Extensions(list):

        def __init__(self, iterable=None):
            """
            Auxiliary class to store valid extensions.
            :param iterable:
            """
            list.__init__(self, [] if iterable is None else [".{}".format(str(i).replace('.', '')) for i in iterable])

        def append(self, value):
            list.append(self, ".{}".format(value.replace('.', '')))

        def __str__(self):
            return '|'.join(str(i) for i in self.__iter__())
