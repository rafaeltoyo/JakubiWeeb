import requests

from ..baseapi import BaseAPI
from ...lyrics import Lyrics

# https://developer.musixmatch.com/documentation


class MusixMatchAPI(BaseAPI):

    def __init__(self, apikey: str, version: str = "1.1"):
        super().__init__(url="https://api.musixmatch.com/ws/{0}/{1}", apikey=apikey)
        self.__version = version

    def get_lyrics(self, search: str) -> Lyrics:
        # Search music by user string
        try:
            search_response = requests.get(self.url.format(self.__version, "track.search"),
                                           params={'apikey': self.apikey, 'q': search})
        except Exception as e:
            print(e)
        else:
            if not BaseAPI.status_code_handler(search_response):
                return ""
            music = search_response.json()
            id = music['message']['body']['track_list'][0]['track']['track_id']

            # Search music lyrics by user string
            response = requests.get(self.url.format(self.__version, "track.lyrics.get"),
                                    params={'apikey': self.apikey, 'track_id': id})
            if not BaseAPI.status_code_handler(response):
                return ""

            lyrics = response.json()
            print(response.json())
            return lyrics['message']['body']['lyrics']['lyrics_body']
