# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

import blog.urls
import analytics.urls


urlpatterns = [
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('admin/', admin.site.urls),
    path('analytics/',include(analytics.urls)),
    path('feedback/', TemplateView.as_view(template_name="feedback.html"), name='feedback'),
    re_path('', include('accounts.urls')),
    re_path('', include(blog.urls)),
]


if settings.HAS_INDEX_PAGE:
    index_template = getattr(settings, 'INDEX_TEMPLATE', 'index.html')
    urlpatterns = [path('', TemplateView.as_view(template_name=index_template), name='index'),] + urlpatterns


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
