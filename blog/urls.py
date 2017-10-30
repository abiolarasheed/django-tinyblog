from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^post/$', views.EntryListView.as_view(), name='entry_list'),
    url(r'^(?P<slug>[-\w]+)/$', views.EntryDetail.as_view(), name='entry_detail'),
]
