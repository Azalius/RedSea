class Song:
    def __init__(self, url):
        pass

    def download(self, path, name=None):
        if name == None:
            name = self["name"]

    def __getattr__(self, item):
        return self.infos[item]

    def __setattr__(self, key, value):
        self.infos[key] = value

