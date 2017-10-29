# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from .models import Entry


class EntryDetail(DetailView):
    model = Entry
