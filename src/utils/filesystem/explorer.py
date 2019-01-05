import sys
import os
import re
from pathlib import Path


class Explorer:

    def __init__(self, path, type="", recursive=True):
        """
        Search for folders or files in the path provided.
        :param path: search path.
        :param type: the extension of the files you want.
                "" or "files": Return all files
                ".xxx" or ".xxx|.yyy|...": Return [.xxx, .yyy, ...] files
                "folder": Return all folders
        """
        self.target = str(Path(path))
        self._type = type
        self.recursive = recursive

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, v: str):
        if v in ["", "folder", "files"] or re.search("^(\\.\\w+)(\\|\\.\\w+)*$", v):
            self._type = v
        else:
            print("Invalid type! Using default type=''.")

    def __iter__(self):
        if self.type == "folder":
            return self.get_folders()
        else:
            return self.get_files()

    def get_folders(self):

        for root, dirs, files in os.walk(self.target):
            for dir in dirs:
                yield Path(root), dir
            if not self.recursive:
                break

    def get_files(self):

        for root, dirs, files in os.walk(self.target):
            for name in files:
                if self.type == "" or self.type == "files" or re.search(self.type + "$", name):
                    path = Path(root) / name
                    yield path
            if not self.recursive:
                break
