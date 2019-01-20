
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import urllib.request
from urllib.parse import urlparse as parse


class AnimeLyrics:

    def __init__(self, keyword):
        self.search_term = keyword
        self.soup: BeautifulSoup
        self.page_url: str
        self.website: str
        self.title: str
        self.lyrics: str

        self.load_results() #Inicializa a busca pela letra

    def load_results(self):
        print("Searching lyrics for [{}]...".format(self.search_term))
        for url in search(self.search_term, tld='com.pk', lang='en', stop=10):
            if parse(url).hostname == 'www.animelyrics.com':
                self._parse_animelyrics(url)
                return
            elif parse(url).hostname == 'www.letras.com' or parse(url).hostname == 'www.letras.mus.br' and url.count('traducao') == 0:
                self._parse_letras(url)
                return
            elif parse(url).hostname == 'www.smule.com':
                self._parse_smule(url)
                return
        print("Searching lyrics for [{}] (2nd try)...".format(self.search_term))
        for url in search(self.search_term+' lyrics', tld='com.pk', lang='en', stop=10):
            if parse(url).hostname == 'www.animelyrics.com':
                self._parse_animelyrics(url)
                return
            elif parse(url).hostname == 'www.letras.com' or parse(url).hostname == 'www.letras.mus.br' and url.count('traducao') == 0:
                self._parse_letras(url)
                return
            elif parse(url).hostname == 'www.smule.com':
                self._parse_smule(url)
                return

    def _parse_animelyrics(self, url):
        self.page_url = url
        self.website = 'animelyrics'
        self.soup = BeautifulSoup(requests.get(self.page_url).text, 'html5lib')
        self.lyrics = ', '.join([div.text.replace('\xa0', ' ').strip() for div in self.soup.find_all('td', {'class': 'romaji'})])
        self.title = self.soup.find_all('h1')[1].get_text()
        print("Found [{}] lyrics on animelyrics.com!".format(self.search_term))

    def _parse_letras(self, url):
        self.page_url = url
        self.website = 'letras.mus'
        html = urllib.request.urlopen(self.page_url).read().decode()
        self.lyrics = html.split('<article>')[1].split('</article>')[0].replace('<p>', '\n').replace('</p>','\n').replace('<br/>', '\n')
        print("Found [{}] lyrics on letras.mus.br!".format(self.search_term))

    def _parse_smule(self, url):
        self.page_url = url
        self.website = 'smule'
        html = urllib.request.urlopen(self.page_url).read().decode()
        self.lyrics = html.split('<div class="lyrics content ">')[1].split('</div>')[0].replace('<p>', '\n').replace('</p>', '\n').replace('<br>', '\n')
        print("Found [{}] lyrics on smule.com!".format(self.search_term))
