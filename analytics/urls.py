# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^analytics.gif$', views.AnalyticsView.as_view(), name='analytics'),
]