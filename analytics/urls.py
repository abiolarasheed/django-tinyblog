# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views


urlpatterns = [path("analytics.gif", views.AnalyticsView.as_view(), name="analytics")]
