from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.EntryDetail.as_view(), name='entry_detail'),
]
