import uuid
import scrapy
import random
import requests
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
        for url in self.urls:
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
                self.log.error("The object data must be instance of SpiderData")
                raise SpiderException('[Error, execute]: The object data must be instance of SpiderData')
        except Exception as e:
            self.log.error(str(e))
            raise SpiderException('[Warning, execute]: %s' % str(e))
        
    def run_spider(self, agent, data):
        """Run the spider asocited to agent.
        @param spider:class Calss of SpiderAction.
        @param data:SpiderData dato to scrape
        """
        def f(q):
            try:
                s = get_project_settings()
                user_agent_list = data.getUserAgentList()
                user_agent = None
                if len(user_agent_list) > 0:
                    user_agent = random.choice(user_agent_list)
                if user_agent:
                    s.update({
                        "LOG_ENABLED": "True",
                        "TELNETCONSOLE_ENABLED": "False",
                        "USER_AGENT": user_agent
                    })
                else:
                    s.update({
                        "LOG_ENABLED": "True",
                        "TELNETCONSOLE_ENABLED": "False"
                    })
                runner = crawler.CrawlerRunner(s)
                configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
                deferred = runner.crawl(
                    agent.class_element, 
                    cus_urls = data.getUrls(),
                    agent = agent
                )
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None)
            except Exception as e:
                q.put(e)
                self.log.error(str(e))
                raise SpiderException('[Warning, execute]: %s' % str(e))
        try:
            q = Queue()
            p = Process(target=f, args=(q,))
            p.start()
            try:
                self.log.info("Inicia la arana %s en el proceso: %s" % (agent.id, str(p)))
                q.get(timeout=120)
                self.log.info("Finaliza la arana %s en el proceso: %s" % (agent.id, str(p)))
            except:
                pass        
            p.kill()
        except Exception as e:
            self.log.error(str(e))
            raise SpiderException('[Warning, execute]: %s' % str(e))

    def send_extern_event(self, gateway, command, data):
        try:
            requests.post(gateway, json = {
                "command": command,
                "dto": data
            })
        except Exception as e:
            self.log.error(str(e))
            raise SpiderException('[Warning, execute]: %s' % str(e))
