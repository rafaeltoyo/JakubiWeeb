import requests
from bs4 import BeautifulSoup

from ..baseapi import BaseAPI, Lyrics

# https://genius.com/api-clients


class GeniusAPI(BaseAPI):

    def __init__(self, apikey: str):
        super().__init__(url="https://api.genius.com{}", apikey=apikey)

    def __search_song(self, search: str):

        try:
            response = requests.get(self.url.format("/search"),
                                    params={'q': search},
                                    headers={'Authorization': 'Bearer {}'.format(self.apikey)})
            if BaseAPI.status_code_handler(response):
                content = response.json()
                hits = content['response']['hits']
                if isinstance(hits, list):
                    for hit in hits:
                        if hit['index'] == "song":
                            return hit['result']
        except Exception as e:
            print(e)
        return None

    def __get_song(self, api_path: str):

        try:
            response = requests.get(self.url.format(api_path),
                                    params={},
                                    headers={'Authorization': 'Bearer {}'.format(self.apikey)})
            if BaseAPI.status_code_handler(response):
                content = response.json()
                return content['response']['song']
        except Exception as e:
            print(e)
        return None

    def get_lyrics(self, search: str):
        if len(search.strip()) <= 0:
            return None

        pre_song = self.__search_song(search)
        if pre_song is None or 'api_path' not in pre_song.keys() or len(pre_song) <= 0:
            return None

        song = self.__get_song(pre_song['api_path'])

        if song is None or 'url' not in song.keys() or len(str(song['url'])) <= 0:
            return None

        try:
            response = requests.get(song['url'])
            if BaseAPI.status_code_handler(response):
                html = BeautifulSoup(response.text, "html.parser")
                lyrics = html.find("div", class_="lyrics").get_text().strip('\n')

                print("Lyrics:")
                print("\tSearch: " + search)
                print("\tURL: " + song['url'])

                return Lyrics(lyrics, song['url'])
        except Exception as e:
            print(e)
        return None
