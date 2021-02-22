"""Module for SeleniumMiddleware scrapy middleware."""
from importlib import import_module
from types import SimpleNamespace

from scrapy import http, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.utils.python import to_bytes
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from twisted.web.client import ResponseFailed

from scrapy_selenium_extended.mixins import AnnotatedAttributesMixin


class SeleniumMiddleware(AnnotatedAttributesMixin):
    """Scrapy middleware to handle requests using selenium."""

    command_executor: str
    driver_executable_path: str
    desired_capabilities: dict = {}
    browser_name: str = ""
    driver_arguments: list = []

    _data = SimpleNamespace()
    _attr_prefix = "selenium_"

    def __init__(self, settings: Settings):
        """Initialize the selenium webdriver."""
        if "SELENIUM_COMMAND_EXECUTOR" in settings:
            self.set_attribute(settings, str, "command_executor")
        elif "SELENIUM_DRIVER_EXECUTABLE_PATH" in settings:
            self.set_attribute(settings, str, "driver_executable_path")
        else:
            raise NotConfigured(
                "One of (SELENIUM_DRIVER_EXECUTABLE_PATH, SELENIUM_COMMAND_EXECUTOR) must be provided"
            )

        self.set_attribute(settings, dict, "desired_capabilities")
        self.set_attribute(settings, str, "browser_name")
        self.set_attribute(settings, list, "driver_arguments")

        self._data.desired_capabilities = self.desired_capabilities
        if self.browser_name:
            driver_options = self._get_driver_options(self.browser_name)
            for argument in self.driver_arguments:
                driver_options.add_argument(argument)
            self._data.desired_capabilities.update(driver_options.to_capabilities())
        # TODO: Raise warning if driver_options but not browser_name

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "SeleniumMiddleware":
        """Initialize the middleware with the crawler settings."""
        middleware = cls(crawler.settings)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request: http.Request, spider: Spider) -> http.Response:
        """Process a request using the selenium driver."""
        driver = self.get_driver()

        try:
            driver.get(request.url)
            url = driver.current_url
            body = to_bytes(driver.page_source)
        except WebDriverException as e:
            raise ResponseFailed(f"WebDriverException {e}")

        return http.HtmlResponse(url=url, body=body, encoding="utf-8", request=request)

    def spider_closed(self) -> None:
        """Shutdown the driver when spider is closed."""
        self.driver.quit()

    def get_driver(self) -> webdriver.Remote:
        """Get driver in use, if is not available request new one."""
        try:
            driver = self.driver
        except AttributeError:
            driver = self._get_driver()
            self.driver = driver
        return driver

    def get_local_driver(self) -> webdriver.Remote:
        """Get local driver."""
        browser_name = self._data.desired_capabilities["browserName"]
        driver_class = self._get_driver_class(browser_name)
        return driver_class(
            executable_path=self._data.executable_path,
            capabilities=self._data.desired_capabilities,
        )

    def get_remote_driver(self) -> webdriver.Remote:
        """Get remote driver."""
        return webdriver.Remote(
            command_executor=self.command_executor,
            desired_capabilities=self._data.desired_capabilities,
        )

    def _get_driver(self) -> webdriver.Remote:
        if self.command_executor is not None:
            return self.get_remote_driver()
        elif self.driver_executable_path is not None:
            return self.get_local_driver()
        raise NotConfigured(
            "One of (SELENIUM_DRIVER_EXECUTABLE_PATH, SELENIUM_COMMAND_EXECUTOR) must be provided"
        )

    def _get_driver_class(self, browser_name: str) -> callable:
        webdriver_base_path = self._webdriver_base_path(browser_name)
        driver_class_module = import_module(f"{webdriver_base_path}.webdriver")
        driver_class = getattr(driver_class_module, "WebDriver")
        return driver_class

    def _get_driver_options(self, browser_name: str) -> object:
        # TODO: Try except (driver name not supported)
        webdriver_base_path = self._webdriver_base_path(browser_name)
        driver_options_module = import_module(f"{webdriver_base_path}.options")
        driver_options_class = getattr(driver_options_module, "Options")
        return driver_options_class()

    def _webdriver_base_path(self, browser_name: str) -> str:
        return f"selenium.webdriver.{browser_name}"
