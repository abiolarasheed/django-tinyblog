# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.generic import TemplateView

import accounts.urls
import analytics.urls
import blog.urls
import blog.views as blog_views
import blog.sitemaps as blog_sitemaps


sitemaps = {
    'static': blog_sitemaps.StaticViewSitemap,
    "blogs": blog_sitemaps.BlogSitemap,
}


urlpatterns = [
    path('about/', TemplateView.as_view(template_name="about.html"),
         name='about'),
    path('admin/', admin.site.urls),
    path('analytics/', include(analytics.urls)),
    re_path('blog/', include(blog.urls)),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
     name='django.contrib.sitemaps.views.sitemap'),
    path('feedback/', TemplateView.as_view(template_name="feedback.html"),
         name='feedback'),
    re_path('', include(accounts.urls)),
]


if settings.HAS_INDEX_PAGE:
    index_template = getattr(settings, 'INDEX_TEMPLATE', 'index.html')
    urlpatterns = [path('', TemplateView.as_view(template_name=index_template), name='index')] + urlpatterns
else:
    urlpatterns = [path('', blog_views.EntryListView.as_view(), name='index')] + urlpatterns


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
