import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse as parse

from app.lyrics.lyrics import Lyrics
from ..website import LyricsWebsite


class AnimeLyrics(LyricsWebsite):

    def __init__(self):
        super().__init__("AnimeLyrics", "www.animelyrics.com")

    def accept(self, url: str):
        return parse(url).hostname in self.urls

    def get_lyrics(self, url: str) -> Lyrics:
        soup = BeautifulSoup(requests.get(url).text, 'html5lib')

        title = soup.find_all('h1')[1].get_text()
        lyrics = ', '.join(
            [div.text.replace('\xa0', ' ').strip() for div in soup.find_all('td', {'class': 'romaji'})])
        content = title + "\n\n" + lyrics
        return Lyrics(url, content)
