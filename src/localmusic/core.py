import re
from sqlite3 import OperationalError, IntegrityError
from typing import List

from .loader import LocalMusicLoader
from .storage import LocalMusicStorage
from .model import Music

from utils.filesystem import Explorer


class LocalMusicController:

    def __init__(self):
        self.music = []  # type: List[Music]

        self.__loader = LocalMusicLoader()
        self.__storage = LocalMusicStorage()

    def __del__(self):
        del self.__loader
        del self.__storage

    def init_db(self):
        num_folder = 0
        num_music = 0

        # Initialize Folder table
        try:
            r = self.__storage.folderDAO.count()

            if isinstance(r, list) and len(r) > 0:
                num_folder = int(r[0][0])
            print("Folders: {}".format(num_folder))

        except OperationalError:
            print("Creating folder table ...")
            self.__storage.folderDAO.create()
        except Exception as e:
            raise e

        # Initialize Music table
        try:
            r = self.__storage.musicDAO.count()

            if isinstance(r, list) and len(r) > 0:
                num_music = int(r[0][0])
            print("Musics: {}".format(num_music))

        except OperationalError:
            print("Creating music table ...")
            self.__storage.musicDAO.create()
        except Exception as e:
            raise e

    def __insert_folder(self, title: str, path: str):
        """
        Save folder data
        :param title: Folder title (without prefix)
        :param path: Folder absolute path
        :return: Folder ID
        """

        print("Folder '{}' ({})".format(title, path))

        try:
            # Try insert folder
            result = self.__storage.folderDAO.insert(title, path)
            print("Insert with success!")
            return int(result)

        except IntegrityError:
            # Treat integrity error: check current folder in database
            return self.__update_folder(title, path)

        except Exception as e:
            print("Error in insert '{}': {}".format(title, e))

    def __update_folder(self, title: str, path: str):
        """
        Update folder path
        :param title: Title for search
        :param path: New absolute path
        :return: Folder ID
        """
        try:
            # Check if folder already exist
            saved_data = self.__storage.folderDAO.select(name=title)

            # Saved data found
            if saved_data is not None and len(saved_data) > 0:
                # Current path is different
                if saved_data[2] != path:
                    # Update folder absolute path
                    print("ALERT: Updating '{}'.".format(title))
                    result = self.__storage.folderDAO.update(title, path)
                    print(result)
                else:
                    print("This folder has no changes!")
                return int(saved_data[0])

            raise Exception("Invalid folder (not found)!")

        except Exception as e:
            print("Error in update '{}': {}".format(title, e))
            return None

    def __insert_music(self, music: Music, folder_id: int):
        """

        :param music:
        :param folder_id:
        :return:
        """
        print(music)

        try:
            # Try insert folder
            result = self.__storage.musicDAO.insert(music, folder_id)
            print("Insert with success!")
            return int(result)

        except IntegrityError:
            # Treat integrity error: ignore
            print("This music already exist!")

        except Exception as e:
            print("Error in insert '{}': {}".format(music.title, e))

    def load(self, path="", n_threads=0):
        self.init_db()
        print("Loading musics in '{}'!".format(path))

        for root, folder in Explorer(path, type="folder", recursive=False):

            # Fix folder title (removing prefix)
            title = re.sub(r'^([@|-] )(.*)$', r'\2', folder)
            # Create absolute path
            path = str(root / folder)

            # Save this folder (or update)
            folder_id = self.__insert_folder(title, path)
            print(folder_id)

            # Valid folder ID returned?
            if folder_id is None or not isinstance(folder_id, int) or folder_id <= 0:
                continue

            # Get all music inside
            for item in self.__loader.load(path):
                # Save these musics
                self.__insert_music(item, folder_id)

        self.__storage.searchToolDAO.create()

    def search_all(self, search, num: int = 20):
        for i in self.__storage.searchToolDAO.select(search=str(search), num=num):
            yield Music(**i)

    def search(self, search):
        search = str(search)

        if re.search('^[0-9]+$', search):
            # search parameter is ID
            for i in self.__storage.searchToolDAO.select(search=int(search)):
                return Music(**i)

        else:
            # search parameter is string
            for i in self.__storage.searchToolDAO.select(search=str(search)):
                return Music(**i)
