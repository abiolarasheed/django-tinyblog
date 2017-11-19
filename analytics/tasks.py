# -*- coding: utf-8 -*-
from datetime import date

from .models import PageView


def save_page_analytics(data):
    today = date.today()

    try:
        PageView.objects.get(url=data['url'],
                             domain=data['domain'],
                             session_id=data['session_id'],
                             timestamp__contains=today)
    except PageView.DoesNotExist:
        page = PageView(**data)
        page.save()
