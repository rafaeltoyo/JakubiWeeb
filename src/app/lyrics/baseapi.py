import abc
import requests


class Lyrics:

    def __init__(self, content: str = "", source: str = ""):
        self.__content = content
        self.__source = source

    @property
    def content(self) -> str:
        return self.__content

    @property
    def source(self) -> str:
        return self.__source


class BaseAPI(metaclass=abc.ABCMeta):

    def __init__(self, url: str, apikey: str):
        self.__url = url
        self.__apikey = apikey

    @staticmethod
    def status_code_handler(response: requests.Response):
        if response.status_code != 200:
            print("Response [Code %d]:" % response.status_code)
            print(response.raw.info())
            print("Error!")
            return False
        return True

    @property
    def url(self) -> str:
        return self.__url

    @property
    def apikey(self) -> str:
        return self.__apikey

    @abc.abstractmethod
    def get_lyrics(self, search: str) -> Lyrics:
        pass
