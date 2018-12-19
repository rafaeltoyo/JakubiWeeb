class Music(object):
    title: str
    filename: str

    def __init__(self, title: str, filename: str):
        self.title = title
        self.filename = filename

    def __str__(self):
        return self.title
