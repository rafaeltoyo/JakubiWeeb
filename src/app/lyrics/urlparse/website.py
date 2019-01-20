import abc
import requests
from typing import List, Any

from ..lyrics import Lyrics


class LyricsWebsite(metaclass=abc.ABCMeta):

    def __init__(self, name: str, url: str, *urls):
        self.__name = name
        self.__urls = [url] + [str(i) for i in urls]

    @staticmethod
    def status_code_handler(response: requests.Response):
        if response.status_code != 200:
            print("Response [Code %d]:" % response.status_code)
            print(response.raw.info())
            print("Error!")
            return False
        return True

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__urls[0]

    @property
    def urls(self) -> List[str]:
        return self.__urls

    @abc.abstractmethod
    def accept(self, url: str) -> bool:
        pass

    @abc.abstractmethod
    def get_lyrics(self, search: str) -> Lyrics:
        pass
