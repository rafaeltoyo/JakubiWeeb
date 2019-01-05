from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from .model import Music
from .exceptions import *


class LocalMusicLoader:

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
            raise LMInvalidExtensionException(msg)
        return path

    def _extract(self, path: Path):
        """
        Extract meta-data from music file like name and artists.
        This method uses mutagen lib to open the file.
        :param path: Path object with filename
        :return: List with meta-data
        """
        # Parameters
        file = None
        title_tag = ""
        artist_tag = ""

        # Return
        data = {
            'title': "",
            'artists': "",
            'duration': 0.0
        }

        # Check sufix and open music file
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
            artist_tag = "artist"

        # Check opening success and read data
        if file is not None:
            # Get music title
            if title_tag in file.keys():
                title = file.get(title_tag)
                data['title'] = (str(title[0] if len(title) > 0 else "")) if isinstance(title, list) else str(title)

            # Get music artists (separated with '/')
            if artist_tag in file.keys():
                artist = file.get(artist_tag)
                data['artists'] = "/".join(artist) if isinstance(artist, list) else str(artist)

            # Get music lenght (seconds)
            data['duration'] = float(file.info.length)

        return data

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
        data = self._extract(path)
        info.name = data['title']
        info.artists = data['artists'].replace("/", " & ")
        info.duration = data['duration']

        return info

    def load(self, path):
        """
        Load and extract info from music folder or files.
        :param path: Music folder path or music filename (relative or absolute path).
        :return: Music info object (iterable)
        """
        # Fix path to absolute
        path = path if isinstance(path, Path) else Path(str(path))
        # Check: path is file or folder
        if path.is_dir():
            # If folder then check each file inside.
            for item in path.iterdir():
                for i in self.load(item):
                    yield i
        else:
            # If file then try to load as music
            try:
                yield self._load_music(path)
            except LMInvalidExtensionException:
                pass

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
