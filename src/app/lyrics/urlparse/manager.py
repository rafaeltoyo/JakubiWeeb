from typing import List, Any
from googlesearch import search as gsearch

from .website import LyricsWebsite


class LyricsSearchManager:

    def __init__(self):
        self.__websites: List[LyricsWebsite] = []

    def add(self, website: LyricsWebsite):
        self.__websites.append(website)

    def search(self, search_term: str):
        # Searching lyrics for <search_term>
        for url in gsearch(search_term, tld='com.pk', lang='en', stop=10):
            for website in self.__websites:
                if website.accept(url):
                    try:
                        print("Lyrics found in {0.name}! ({0.url})".format(website))
                        return website.get_lyrics(url)
                    except Exception as e:
                        print(e)
                        continue

        # Improve search accuracy (2nd try)
        if not search_term.find("lyrics"):
            return self.search(search_term + " lyrics")
        return None
