import uuid
import scrapy
import requests
import multiprocessing
from abc import abstractmethod
from .SpiderData import SpiderData
import scrapy.crawler as crawler
from twisted.internet import reactor
from .exceptions import SpiderException
from ..kernel.agent.Action import Action
from multiprocessing import Process, Queue
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class SpiderAction(Action, scrapy.Spider):
    
    def __init__(self, cus_urls = "", agent = None):
        self.urls = cus_urls
        self.name = str(uuid.uuid1())
        super().__init__()
        if agent:
            self.agent = agent
            self.log = agent.log
    
    def start_requests(self):
        """Makes the request urls"""
        #print("Entra", self.agent.id)
        for url in self.urls:
            #print("Entra**")
            yield scrapy.Request(url, callback = self.execute_parse)

    @abstractmethod
    def execute_parse(self, response):
        pass

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        try:
            if isinstance(data, SpiderData):
                self.agent.state['data'] = data
                self.run_spider(self.agent, data)
            else:
                raise SpiderException('[Error, execute]: The object data must be instance of SpiderData')
        except Exception as e:
            raise SpiderException('[Warning, execute]: %s' % str(e))
        
    def run_spider(self, agent, data):
        """Run the spider asocited to agent.
        @param spider:class Calss of SpiderAction.
        @param data:SpiderData dato to scrape
        """
        def f(q):
            try:
                s = get_project_settings()
                s.update({
                    "LOG_ENABLED": "False",
                    "TELNETCONSOLE_ENABLED": "False",
                    "USER_AGENT":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                })
                runner = crawler.CrawlerRunner(s)
                """
                configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
                runner = crawler.CrawlerRunner()
                """
                #print("Aja 1", data.__dict__)
                deferred = runner.crawl(
                    agent.class_element, 
                    cus_urls = data.getUrls(),
                    agent = agent
                )
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None)
            except Exception as e:
                #print("ERR$$$$$$$$$$$$$: ", e)
                q.put(e)
                raise SpiderException('[Warning, execute]: %s' % str(e))
        try:
            #print(multiprocessing.current_process())
            q = Queue()
            p = Process(target=f, args=(q,))
            p.start()
            try:
                print("INI", agent.id, p)
                result = q.get(timeout=120)
                #print("END", agent.id, p)
            except:
                #print("END*", agent.id, p)
                pass        
            #p.join()
            #p.terminate()
            p.kill()
            #if result is not None:
            #    raise result
        except Exception as e:
            #print("ERR#############: ", e)
            raise SpiderException('[Warning, execute]: %s' % str(e))

    def send_extern_event(self, gateway, command, data):
        try:
            requests.post(gateway, json = {
                "command": command,
                "dto": data
            })
        except Exception as e:
            raise SpiderException('[Warning, execute]: %s' % str(e))
