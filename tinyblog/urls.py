# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

import blog.urls
import analytics.urls


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='index'),
    url(r'^', include('accounts.urls')),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),
    url(r'^feedback/$', TemplateView.as_view(template_name="feedback.html"), name='feedback'),
    url(r'^blog/', include(blog.urls)),
    url(r'^analytics/',include(analytics.urls)),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
