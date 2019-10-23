from django.conf import settings


def brand(request) -> dict:
    """
    Create brand name in navbar
    """
    context = {"brand": settings.NAVBAR_BRAND}
    return context
