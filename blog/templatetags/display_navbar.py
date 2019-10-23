from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.urls import reverse_lazy


register = template.Library()


class NavBarLink:
    """
    Creates link to use for narbar
    """
    def __init__(self, **kwargs):
        self.label = kwargs.get("label")
        self.url = reverse_lazy(kwargs.get("url_name"), args=kwargs.get("url_args"))


@register.simple_tag
def nav_bar_links() -> list:
    """
    Creates a list of links for the navbar
    """
    if settings.NAVBAR_LINKS:
        links = [NavBarLink(**lnk) for lnk in settings.NAVBAR_LINKS]
        return links
    return list()
