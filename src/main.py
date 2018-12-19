from mutagen.mp3 import MP3

from utils.db import Database
from utils.loader.loader import FileLoader
from utils.config import Config

BASEPATH = "D://Rafael//Music//Others//Anime Musics//Opening + Ending"

Config()

exit(0)

print('=' * 80)
fl = FileLoader(path=BASEPATH)
for anime in fl.search_animes():
    print('-' * 80)
    print(anime.name)
    for music in anime:
        mp3 = MP3(music.filename)

        print('- ' * 40)
        print(music.title)
        print('.' * 10)
        print(mp3.get('TIT2'))
        print('.' * 10)
        print(mp3.get('TPE1'))
