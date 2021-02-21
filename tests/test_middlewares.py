"""Module for testing ``scrapy_webdriver`` middlewares."""
from unittest import TestCase

from scrapy import Crawler

from scrapy_webdriver import middlewares


class BaseScrapyTestCase(TestCase):
    """Base test case."""

    class SimpleSpider(scrapy.Spider):
        name = 'simple_spider'
        allowed_domains = ['python.org']
        start_urls = ['http://python.org']

        def parse(self, response):
            pass
    
    @classmethod
    def setUpClass(cls):
        cls.settings = {}
        cls.spider_class = cls.SimpleSpider
    

class SeleniumMiddlewareTestCase(BaseScrapyTestCase):
    """Test case for SeleniumMiddleware."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.settings.update({
            'SELENIUM_COMMAND_EXECUTER': ''
        })

        crawler = cls._mock_crawler()

        cls.selenium_middleware = middlewares.SeleniumMiddleware.from_crawler(crawler)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.selenium_middleware.driver.quit()

    @classmethod
    def _mock_crawler(cls):
        return Crawler(spidercls=cls.spider_class, settings=cls.settings)
