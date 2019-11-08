from django.conf import settings


def navbar(request) -> dict:
    """
    Create brand name in navbar
    """
    context = {
        "brand": settings.NAVBAR_BRAND,
        "navbar_backgroud_color": settings.NAVBAR_BACKGROUND_COLOR,
        "navbar_border_color": settings.NAVBAR_BORDER_COLOR,
    }
    return context
