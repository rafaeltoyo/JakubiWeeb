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

        lyrics = ""
        for div in soup.find_all('td', {'class': 'romaji'}):
            div.find('dt').extract()
            lyrics += div.find('span', {'class', 'lyrics'}).text.replace('\xa0', ' ').strip() + "\n\n"

        if len(lyrics.replace('\n', '')) == 0:
            top_split = soup.find('div', {'class', 'centerbox'}).find('dt').text

            [i.extract() for i in soup.find('div', {'class', 'centerbox'}).find_all('p')]
            [i.extract() for i in soup.find('div', {'class', 'centerbox'}).find_all('script')]

            first_split = soup.find('div', {'class', 'centerbox'}).text.split(top_split)
            if len(first_split) < 2:
                return None
            lyrics = first_split[1].replace('\xa0', ' ').strip()

        title = soup.find_all('h1')[1].get_text()
        content = title + "\n\n" + lyrics
        return Lyrics(content, url)
