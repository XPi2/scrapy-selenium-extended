"""Module for mixins."""
from typing import Any

from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings


class AnnotatedAttributesMixin:
    """Mixin of annotated attributes methods for the middlewares."""

    _attr_prefix = ""

    def set_attribute(self, settings: Settings, type_: type, key: str, default=None) -> None:
        """Set attribute from settings with type validation."""
        default_ = getattr(self, key, default)  # Default value
        setting_key = f"{self._attr_prefix}{key}".upper()
        if default_ is None and setting_key not in settings:
            raise NotConfigured(f"{setting_key} has to be set.")

        value = self.get_from_settings(settings, type_, setting_key, default_)
        setattr(self, key, value)

    def get_from_settings(self, settings: Settings, type_: type, *a, **kw) -> Any:
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
