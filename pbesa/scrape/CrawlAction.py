import uuid
import scrapy
import random
from abc import abstractmethod
import scrapy.crawler as crawler
from .CrawlData import CrawlData
from twisted.internet import reactor
from scrapy.spiders import CrawlSpider
from .exceptions import SpiderException
from ..kernel.agent.Action import Action
from multiprocessing import Process, Queue
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class CrawlAction(Action, CrawlSpider):
    
    def __init__(self, cus_urls = [], cus_allowed_domains = [], agent = None):
        self.start_urls = cus_urls
        self.allowed_domains = cus_allowed_domains
        self.name = str(uuid.uuid1())
        super().__init__()
        if agent:
            self.agent = agent
            self.log = agent.log

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        try:
            if isinstance(data, CrawlData):
                self.run_spider(self.agent, data)
            else:
                self.log.error("The object data must be instance of SpiderData")
                raise SpiderException('[Error, execute]: The object data must be instance of SpiderData')
        except Exception as e:
            raise SpiderException('[Warning, execute]: %s' % str(e))

    @abstractmethod
    def case_without_rules_trigger(self):
        pass
        
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
                configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
                runner = crawler.CrawlerRunner(s)
                agent.state['fire'] = False
                agent.state['data'] = data
                deferred = runner.crawl(
                    agent.class_element, 
                    cus_urls = data.getUrls(),
                    cus_allowed_domains = data.getAllowedDomains(),
                    agent = agent
                )
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                if not agent.state['fire']:
                    q.put(self.case_without_rules_trigger())
                q.put(None)
            except Exception as e:
                q.put(e)
                self.log.error(str(e))
                raise SpiderException('[Warning, execute]: %s' % str(e))
        try:
            q = Queue()
            p = Process(target=f, args=(q,))
            p.start()
            self.log.info("Inicia la arana en el proceso: %s" % str(p))
            result = q.get()
            self.log.info("Finaliza la arana en el proceso: %s" % str(p))
            p.join()
            if result is not None:
                data.setUrls(result)
                q = Queue()
                p = Process(target=f, args=(q,))
                p.start()
                self.log.info("Inicia replica de la arana en el proceso: %s" % str(p))
                result = q.get()
                self.log.info("Finaliza replica de la arana en el proceso: %s" % str(p))
                p.join()
        except Exception as e:
            self.log.error(str(e))
            raise SpiderException('[Warning, execute]: %s' % str(e))
