from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

class CrawlData():

    def __init__(
        self, 
        urls = None, 
        allowed_domains = None, 
        rules = None,
        user_agent_list = None
    ):
        self.__urls = None
        self.__rules = None
        self.__user_agent_list = None
        self.__allowed_domains = None
        if not urls:
            self.__urls = []
        if not rules:
            self.__rules = ()
        if not allowed_domains:
            self.__allowed_domains = []

    def addRule(self, rule):
        self.__rules += (rule,)

    def addLinkExtractorRule(self, pattern):
        self.__rules += (Rule(LinkExtractor(restrict_text=(pattern, )), callback='execute_parse'),)
    
    def getRules(self):
        return self.__rules

    def setUrls(self, urls):
        self.__urls = urls

    def addUrl(self, url):
        self.__urls.append(url)

    def getUrls(self):
        return self.__urls

    def setAllowedDomains(self, allowed_domains):
        self.__allowed_domains = allowed_domains

    def addAllowedDomain(self, allowed_domain):
        self.__allowed_domains.append(allowed_domain)

    def getAllowedDomains(self):
        return self.__allowed_domains

    def setUserAgentList(self, user_agent_list):
        self.__user_agent_list = user_agent_list

    def getUserAgentList(self):
        return self.__user_agent_list
