class Music(dict):

    def __init__(self, title: str = "", filename: str = "", name: str = "", artists: str = ""):
        super().__init__(title=title, filename=filename, name=name, artists=artists)

    @property
    def title(self) -> str:
        return str(self["title"])

    @title.setter
    def title(self, v: str):
        self["title"] = v

    @property
    def filename(self) -> str:
        return str(self["filename"])

    @filename.setter
    def filename(self, v: str):
        self["filename"] = v

    @property
    def name(self) -> str:
        return str(self["name"])

    @name.setter
    def name(self, v: str):
        self["name"] = v

    @property
    def artists(self) -> str:
        return str(self["artists"])

    @artists.setter
    def artists(self, v: str):
        self["artists"] = v

    def __str__(self):
        return "Music: '{0[name]}' by *{0[artists]}* ({0[filename]})".format(self)
