import os
import datetime
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from utils.config import Config
from utils.loader import FileLoader
from utils.log import Log


music = FLAC("../01 Kimi No Tonari.flac")
print(music['title'])
print(music['artists'])

music = MP4("../Karakai Jouzu no Takagi-san END 1.m4a")
print(music['©ART'])
print(music['©nam'])

print(os.path.splitext("../Karakai Jouzu no Takagi-san END 1.m4a"))

exit(0)

cf = Config()

fileloader = FileLoader(path=cf.config.music_folder)

for anime in fileloader.search_file(ext="mp3|m4a|flac"):
    print(anime)

print(datetime.date.today() == datetime.date(2018, 12, 26))

Log().set_config(cf)
Log().err("quero")
