# -*- coding: utf-8 -*-
from collections import OrderedDict
from urllib.parse import urlencode

from django.conf import settings
from django.http.response import JsonResponse
from django.views.generic import DetailView, ListView, CreateView

from haystack.views import SearchView

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
    template_name = 'entry_list.html'
    context_object_name = 'entries'
    paginate_by = 12
    model = Entry
    queryset = model.objects.filter(is_published=True).order_by('-modified_at')

    def get_context_data(self, **kwargs):
        context = super(EntryListView, self).get_context_data(**kwargs)
        context['title'] = "My Blog list"
        return context


class JsonSearchView(SearchView):
    def build_absolute_uri(self, page_num, empty_on_1=False):
        host = self.request.get_host()
        path = self.request.path
        scheme = self.request.scheme

        if page_num <= 1:
            if empty_on_1:
                return ""
            page_num = 1

        page = page_num
        q = self.request.GET.get('q', '')
        url = "{}://{}{}?".format(scheme, host, path)

        params = urlencode(OrderedDict(q=q, page=page))
        absolute_uri = "{}{}".format(url, params)
        return absolute_uri

    def build_pager(self, page, paginator):
        next_ = previous = 1

        if page.has_previous():
            previous = page.previous_page_number()

        if page.has_next():
            next_ = page.next_page_number()

        current = page.number
        total = paginator.count

        return dict(total=total, current=self.build_absolute_uri(current),
                    next=self.build_absolute_uri(next_, empty_on_1=settings.EMPTY_ON_1),
                    previous=self.build_absolute_uri(previous, empty_on_1=settings.EMPTY_ON_1))

    def create_response(self):
        context = self.get_context()

        page = context.pop('page')
        paginator = context.pop('paginator')
        suggestion = context.pop('suggestion')

        results = [i.object.as_json() for i in page.object_list]
        context = dict(suggestion=suggestion, results=results)
        context.update(self.build_pager(page, paginator))

        return JsonResponse(context)

    render_json_response = create_response
