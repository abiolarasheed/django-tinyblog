# -*- coding: utf-8 -*-
from django.urls import path

from . import views


urlpatterns = [
    path('analytics.gif', views.AnalyticsView.as_view(), name='analytics'),
]
