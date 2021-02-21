"""Module for common utils."""
from typing import Any

from scrapy.settings import Settings


def get_from_settings(settings: Settings, type_: type, *a, **kw) -> Any:
    """Get value from scrapy Settings with type validation."""
    if type_ is int:
        return settings.getint(*a, **kw)
    elif type_ is bool:
        return settings.getbool(*a, **kw)
    elif type_ is list:
        return settings.getlist(*a, **kw)
    elif type_ is dict:
        return settings.getdict(*a, **kw)
    else:
        return settings.get(*a, **kw)
