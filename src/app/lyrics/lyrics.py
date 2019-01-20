
class Lyrics:

    def __init__(self, content: str = "", source: str = ""):
        self.__content = content
        self.__source = source

    @property
    def content(self) -> str:
        return self.__content

    @property
    def source(self) -> str:
        return self.__source
