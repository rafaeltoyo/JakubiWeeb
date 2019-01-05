class Music(dict):

    def __init__(self,
                 idt: int = 0,
                 title: str = "",
                 filename: str = "",
                 name: str = "",
                 artists: str = "",
                 duration: float = 0.0):
        super().__init__(
            idt=int(idt),
            title=str(title),
            filename=str(filename),
            name=str(name),
            artists=str(artists),
            duration=float(duration))

    @property
    def idt(self) -> int:
        return int(self['idt'])

    @idt.setter
    def idt(self, v: int):
        self['idt'] = v

    @property
    def title(self) -> str:
        return str(self['title'])

    @title.setter
    def title(self, v: str):
        self['title'] = v

    @property
    def filename(self) -> str:
        return str(self['filename'])

    @filename.setter
    def filename(self, v: str):
        self['filename'] = v

    @property
    def name(self) -> str:
        return str(self['name'])

    @name.setter
    def name(self, v: str):
        self['name'] = v

    @property
    def artists(self) -> str:
        return str(self['artists'])

    @artists.setter
    def artists(self, v: str):
        self['artists'] = v

    @property
    def duration(self) -> float:
        return float(self['duration'])

    @duration.setter
    def duration(self, v: float):
        self['duration'] = v

    @property
    def full_title(self) -> str:
        return "[{0[idt]}] '{0[name]}' ({0.title})".format(self)

    def __str__(self):
        minutes, seconds = divmod(self.duration, 60)
        duration = (int(minutes), int(seconds),)
        return "[{0[idt]}] '{0[name]}' by *{0[artists]}* [{1[0]}min {1[1]}sec] ({0[title]})".format(self, duration)
