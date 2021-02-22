# Scrapy Selenium Extended

Scrapy plugin to handle javascript pages with Selenium webdrivers.

Inspired by:

- [clemfromspace/scrapy-selenium](https://github.com/clemfromspace/scrapy-selenium)
- [scrapy-plugins/scrapy-headless](https://github.com/scrapy-plugins/scrapy-headless)

## Installation

...

## Usage

This Scrapy plugin as most of the plugins is managed through scrapy settings.

Set the browser to use, the path to the driver executable and the arguments to pass to the executable:

```python
from shutil import which

SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
SELENIUM_BROWSER_NAME = 'firefox'
SELENIUM_DRIVER_ARGUMENTS = ['-headless']
```

In order to use a remote Selenium driver, specify `SELENIUM_COMMAND_EXECUTOR` instead of `SELENIUM_DRIVER_EXECUTABLE_PATH`:

```python
SELENIUM_COMMAND_EXECUTOR = 'http://localhost:4444'
```

### SeleniumMiddleware

Add the SeleniumMiddleware to the downloader middlewares section of your project settings:

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapy_webdriver.SeleniumMiddleware': 800
}
```

### SeleniumDownloadHandler

...

## Further configuration

You can tweak your driver more in detail using `SELENIUM_DESIRED_CAPABILITIES`. Take into consideration that both `SELENIUM_BROWSER_NAME` and `SELENIUM_DRIVER_ARGUMENTS` can overwrite some of your DesiredCapabilities if you use them at the same time.

For example to get a basic firefox headless driver as the example above using capabilities you only will need to add to the settings:

```python
SELENIUM_DESIRED_CAPABILITIES = {
    'browserName': 'firefox', 'marionette': True, 'acceptInsecureCerts': True, 'moz:firefoxOptions': {'args': ['-headless']}
    }
```
