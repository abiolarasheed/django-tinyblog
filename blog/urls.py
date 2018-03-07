# -*- coding: utf-8 -*-

from django.urls import path

from . import views
from .utils import ajax_required


urlpatterns = [
    path('', views.EntryListView.as_view(), name='entry_list'),
    path('post-in-category/<int:pk>/', views.EntryByCategoryListView.as_view(),
         name='post-in-category'),
    path('category-list', views.CategoryListView.as_view(), name="category-list"),
    path('delete-category/<int:pk>/', views.CategoryDeleteView.as_view(), name="delete-category"),
    path('image/<int:pk>/', views.ImageDetailView.as_view(), name='image_detail'),
    path('image/create/', views.ImageCreateView.as_view(), name='image_create'),
    path('create/', views.EntryCreateView.as_view(), name='entry_create'),
    path('update/<int:pk>/', views.EntryUpdateView.as_view(), name='entry_update'),
    path('publish/<int:pk>/', views.PublishEntryView.as_view(), name='publish_entry'),
    path('unpublish/<int:pk>/', views.UnPublishEntryView.as_view(), name='unpublish_entry'),
    path('search/', ajax_required(views.JsonSearchView()), name='navbar_search'),
    path('<slug:slug>/', views.EntryDetail.as_view(), name='entry_detail'),
]

