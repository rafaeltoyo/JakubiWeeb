import datetime

from utils.config import Config
from utils.loader import FileLoader
from utils.log import Log


cf = Config()

fileloader = FileLoader(path=cf.config.music_folder)

for anime in fileloader.search_file(ext="mp3|m4a|flac"):
    print(anime)

print(datetime.date.today() == datetime.date(2018, 12, 26))

Log().set_config(cf)
Log().err("quero")
