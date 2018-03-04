# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Entry, Image


admin.site.register(Entry)
admin.site.register(Image)
