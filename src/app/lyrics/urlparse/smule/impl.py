import urllib.request
from urllib.parse import urlparse as parse

from app.lyrics.lyrics import Lyrics
from ..website import LyricsWebsite


class Smule(LyricsWebsite):

    def __init__(self):
        super().__init__("Smule", "www.smule.com")

    def accept(self, url: str):
        return parse(url).hostname in self.urls

    def get_lyrics(self, url: str) -> Lyrics:
        html = urllib.request.urlopen(url).read().decode()
        lyrics = html.split('<div class="lyrics content ">')[1].split('</div>')[0].replace('<p>', '\n').replace(
            '</p>', '\n').replace('<br>', '\n')
        return Lyrics(lyrics, url)
