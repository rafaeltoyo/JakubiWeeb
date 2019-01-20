import urllib.request
from urllib.parse import urlparse as parse

from app.lyrics.lyrics import Lyrics
from ..website import LyricsWebsite


class LetrasMus(LyricsWebsite):

    def __init__(self):
        super().__init__("Letras", "www.letras.com", "www.letras.mus.br")

    def accept(self, url: str):
        return parse(url).hostname in self.urls and url.count("traducao") == 0

    def get_lyrics(self, url: str) -> Lyrics:
        html = urllib.request.urlopen(url).read().decode()
        lyrics = html.split('<article>')[1].split('</article>')[0].replace('<p>', '\n').replace('</p>', '\n').replace(
            '<br/>', '\n')
        return Lyrics(url, lyrics)
