"""Module for SeleniumMiddleware scrapy middleware."""
from scrapy import http
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.utils.python import to_bytes
from selenium import webdriver

from scrapy_webdriver.utils import get_from_settings


class SeleniumMiddleware:
    """Scrapy middleware to handle requests using selenium."""

    command_executor: str

    def __init__(self, settings: Settings):
        """Initialize the selenium webdriver."""
        for key, type_ in self.__annotations__.items():
            self._set_attribute(settings, type_, key)
        
        self.get_driver()

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "SeleniumMiddleware":
        """Initialize the middleware with the crawler settings."""
        middleware = cls(crawler.settings)

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware
    
    def process_request(self, request: http.Request, spider: Spider) -> http.Response:
        """Process a request using the selenium driver."""
        driver = self.get_driver()

        driver.get(request.url)
        url = driver.current_url
        body = to_bytes(driver.page_source)

        return http.HtmlResponse(url=url, body=body, encoding="utf-8", request=request)

    def spider_closed(self) -> None:
        """Shutdown the driver when spider is closed."""
        self.driver.quit()
    
    def get_driver(self):
        """Get remote driver."""
        try:
            self.driver # TODO: Check for something reliable
        except AttributeError:
            driver = webdriver.Remote(
                command_executor=self.command_executor
            )
            self.driver = driver
        return self.driver
        
    def _set_attribute(self, settings: Settings, type_: type, key: str) -> None:
        default = getattr(self, key, None)  # Default value
        setting_key = f"selenium_{key}".upper()
        if not default and setting_key not in settings:
            raise NotConfigured(f"{setting_key} has to be set.")

        value = get_from_settings(settings, type_, setting_key, default)
        setattr(self, key, value)
