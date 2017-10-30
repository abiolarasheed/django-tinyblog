# -*- coding: utf-8 -*-
from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView

from .models import Entry


class EntryDetail(DetailView):
    template_name = 'entry_detail.html'
    context_object_name = 'entry'
    model = Entry

    def get_context_data(self, **kwargs):
        context = super(EntryDetail, self).get_context_data(**kwargs)
        context['title'] = context['entry'].title
        return context


class EntryListView(ListView):
    model = Entry
    queryset = model.objects.filter(is_published=True)
