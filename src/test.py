from utils.config import Config
from utils.loader import FileLoader


cf = Config()

fileloader = FileLoader(path=cf.config.music_folder)

for anime in fileloader.search_m4a():
    print(anime)
