"""Module for testing ``scrapy_webdriver`` middlewares."""
from unittest import TestCase
from unittest.mock import Mock

from scrapy import Spider
from scrapy.utils.test import get_crawler
from selenium import webdriver

from scrapy_webdriver import middlewares


class BaseScrapyTestCase(TestCase):
    """Base test case."""

    class SimpleSpider(Spider):
        name = "simple_spider"
        allowed_domains = ["python.org"]
        start_urls = ["http://python.org"]

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
        """Set up base class and update secrets before any test."""
        super().setUpClass()
        cls.settings.update(
            {
                "SELENIUM_COMMAND_EXECUTOR": "http://localhost:4444",
                "SELENIUM_CAPABILITIES": webdriver.DesiredCapabilities.FIREFOX,
            }
        )

    def test_selenium_from_crawler(self):
        """Test initialization of driver from crawler."""
        crawler = self._mock_crawler(self.spider_class, self.settings)
        selenium_middleware = middlewares.SeleniumMiddleware.from_crawler(crawler)

        self.assertIsNotNone(selenium_middleware.command_executor)

    def test_selenium_spider_close(self):
        """Test that driver closes on spider close."""
        crawler = self._mock_crawler(self.spider_class, self.settings)
        selenium_middleware = middlewares.SeleniumMiddleware.from_crawler(crawler)

        mock_driver = Mock()
        selenium_middleware.driver = mock_driver
        selenium_middleware.spider_closed()

        mock_driver.quit.assert_called_once()

    def _mock_crawler(self, spider, settings=None):
        class MockedDownloader(object):
            slots = {}

        class MockedEngine(object):
            downloader = MockedDownloader()
            fake_spider_closed_result = None

            def close_spider(self, spider, reason):
                self.fake_spider_closed_result = (spider, reason)

        crawler = get_crawler(spider, settings)
        crawler.engine = MockedEngine()
        return crawler
