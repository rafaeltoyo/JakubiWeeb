
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import urllib.request
from urllib.parse import urlparse as parse

class AnimeLyrics:

    def __init__(self, keyword):
        self.search_term = keyword
        self.soup:BeautifulSoup
        self.page_url:str
        self.website:str
        self.title:str
        self.lyrics:str

        self.load_results()

    def load_results(self):
        for url in search(self.search_term, tld='com.pk', lang='en', stop=10):
            if parse(url).hostname == 'www.animelyrics.com':
                self.page_url = url
                self.website = 'animelyrics'
                self.soup = BeautifulSoup(requests.get(self.page_url).text, 'html5lib')
                self.lyrics = ', '.join([div.text.replace('\xa0', ' ').strip() for div in self.soup.find_all('td', {'class': 'romaji'})])
                self.title = self.soup.find_all('h1')[1].get_text()
                break
            elif parse(url).hostname == 'www.letras.com':
                self.page_url = url
                self.website = 'letras.mus'
                html = urllib.request.urlopen(self.page_url).read().decode()
                self.lyrics = html.split('<article>')[1].split('</article>')[0].replace('<p>','\n').replace('</p>', '\n').replace('<br/>', '\n')
                break
