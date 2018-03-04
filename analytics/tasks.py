# -*- coding: utf-8 -*-
from datetime import date

from tinyblog import celery_app
from .models import PageView


@celery_app.task(ignore_result=True,
                 name="page_analytics")
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
