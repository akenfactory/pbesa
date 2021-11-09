class SpiderData():

    def __init__(self, urls = None):
        self.__urls = None
        if not urls:
            self.__urls = []
    
    def setUrls(self, urls):
        self.__urls = urls

    def addUrl(self, url):
        self.__urls.append(url)

    def getUrls(self):
        return self.__urls
