class SpiderData():

    def __init__(self, urls = None):
        self.__urls = None
        self.__user_agent_list = None
        if not urls:
            self.__urls = []
    
    def setUrls(self, urls):
        self.__urls = urls

    def addUrl(self, url):
        self.__urls.append(url)

    def getUrls(self):
        return self.__urls
    
    def setUserAgentList(self, user_agent_list):
        self.__user_agent_list = user_agent_list

    def getUserAgentList(self):
        return self.__user_agent_list
