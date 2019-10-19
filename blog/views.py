# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from collections import OrderedDict
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, DeleteView
from django.views.generic.edit import UpdateView

from haystack.views import SearchView
from meta.views import Meta

from blog.models import Category
from blog.utils import ajax_required
from .models import Entry, Image


class PageMetaData:
    def get_meta(self, context=None):
        if context is not None and hasattr(context, "title"):
            _title = context["title"]

        else:
            _title = settings.DEFAULT_META_TITLE

        return Meta(
            title=_title,
            url=self.request.path,
            description=settings.DEFAULT_META_DESCRIPTION,
            image=settings.DEFAULT_META_IMAGE,
            keywords=settings.DEFAULT_META_KEYWORDS,
        )


@method_decorator(login_required(), name="dispatch")
class EntryCreateView(CreateView):
    model = Entry
    success_url = reverse_lazy("entry_list")
    fields = ["category", "title", "poster", "body", "tags"]
    template_name = "entry_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(EntryCreateView, self).form_valid(form)

    def form_invalid(self, form):
        super(EntryCreateView, self).form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def get_success_url(self):
        return reverse_lazy("entry_update", kwargs={"pk": self.object.pk})


@method_decorator(login_required(), name="dispatch")
class EntryUpdateView(UpdateView):
    template_name = "entry_create.html"
    model = Entry
    fields = ("title", "tags", "poster", "body", "is_published")

    def get_context_data(self, **kwargs):
        context = super(EntryUpdateView, self).get_context_data(**kwargs)
        form = context["form"]
        del form.fields["is_published"]
        context["form"] = form
        context["title"] = "Dashboard"
        return context


@method_decorator(login_required, name="dispatch")
class UnPublishEntryView(View):
    def get(self, request, pk):
        try:
            entry = Entry.published.get(author=request.user, pk=pk)
            entry.is_published = False
            entry.save()
            messages.success(request, _("Unpublished Successfully."))
        except Entry.DoesNotExist:
            messages.error(request, _("Unpublish Error!"))
        finally:
            return redirect(reverse_lazy("dashboard-entries"))


@method_decorator(login_required, name="dispatch")
class PublishEntryView(View):
    def get(self, request, pk):
        try:
            entry = Entry.objects.select_related("author").get(
                author=request.user, pk=pk
            )
            entry.is_published = True
            entry.save()
            messages.success(request, _("Article Successfully Published."))
        except Entry.DoesNotExist:
            messages.error(request, _("An error occurred while publishing article!"))
        finally:
            return redirect(reverse_lazy("dashboard-entries"))


class EntryDetail(DetailView):
    context_object_name = "entry"
    model = Entry
    template_dir = os.environ.get("CUSTOM_TEMPLATE_DIR")

    def get_template_names(self):
        if self.template_dir:
            return f"{self.template_dir}/entry_detail.html"
        return "entry_detail.html"

    def get_object(self, queryset=None):
        if self.kwargs.get("slug", None) is None:
            raise Http404

        try:
            return self.model.objects.select_related("author").get(
                author=self.request.user, slug=self.kwargs.get("slug")
            )
        except (self.model.DoesNotExist, TypeError):
            obj = get_object_or_404(
                self.model, slug=self.kwargs.get("slug"), is_published=True
            )
            return obj

    def get_context_data(self, **kwargs):
        entry = self.get_object()
        entry.__class__.objects.select_related("author").filter(pk=entry.pk).update(
            views=F("views") + 1
        )
        context = super(EntryDetail, self).get_context_data(**kwargs)
        context["title"] = context["entry"].title
        context["meta"] = entry.as_meta()
        if settings.CATEGORIES_IN_DETAIL:
            context["categories"] = Category.objects.all().order_by("name")
        return context


class EntryListView(PageMetaData, ListView):
    paginate_by = 12
    model = Entry
    context_object_name = "entries"
    template_dir = os.environ.get("CUSTOM_TEMPLATE_DIR")

    def get_queryset(self):
        return self.model.published.select_related("category").all().order_by("-modified_at")

    def get_template_names(self):
        if self.template_dir:
            return f"{self.template_dir}/entry_list.html"
        return "entry_list.html"

    def get_context_data(self, **kwargs):
        context = super(EntryListView, self).get_context_data(**kwargs)
        context["title"] = _("Latest Posts")
        context["meta"] = self.get_meta(context=context)
        return context


@method_decorator(ajax_required, name="dispatch")
class ImageDetailView(DetailView):
    template_name = "entry_detail.html"
    context_object_name = "image"
    model = Image

    def get(self, request, *args, **kwargs):
        image = self.get_object()
        return JsonResponse(image.as_json())


@method_decorator(login_required(), name="dispatch")
@method_decorator(ajax_required, name="dispatch")
class ImageCreateView(CreateView):
    model = Image
    fields = ["caption", "photo", "entry"]

    def form_invalid(self, form):
        super(ImageCreateView, self).form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        super(ImageCreateView, self).form_valid(form)
        return JsonResponse(self.object.as_json(), status=201)


class JsonSearchView(SearchView):
    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(JsonSearchView, self).dispatch(*args, **kwargs)

    def build_absolute_uri(self, page_num, empty_on_1=False):
        host = self.request.get_host()
        path = self.request.path
        scheme = self.request.scheme

        if page_num <= 1:
            if empty_on_1:
                return ""
            page_num = 1

        page = page_num
        q = self.request.GET.get("q", "")
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

        return dict(
            total=total,
            current=self.build_absolute_uri(current),
            next=self.build_absolute_uri(next_, empty_on_1=settings.EMPTY_ON_1),
            previous=self.build_absolute_uri(previous, empty_on_1=settings.EMPTY_ON_1),
        )

    def create_response(self):
        context = self.get_context()

        page = context.pop("page")
        paginator = context.pop("paginator")
        suggestion = context.pop("suggestion")

        results = [i.object.as_json() for i in page.object_list]
        context = dict(suggestion=suggestion, results=results)
        context.update(self.build_pager(page, paginator))

        return JsonResponse(context)

    render_json_response = create_response


@method_decorator(login_required(), name="dispatch")
class CategoryListView(CreateView, ListView):
    template_name = "category_list.html"
    context_object_name = "categories"
    paginate_by = 30
    model = Category
    success_url = reverse_lazy("category-list")
    fields = ["name"]
    queryset = model.objects.all().order_by("name")

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context["title"] = _("Categories")
        return context


@method_decorator(login_required(), name="dispatch")
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "category_list.html"
    success_url = reverse_lazy("category-list")
    success_message = _("The Category has been deleted successfully.")

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class EntryByCategoryListView(EntryListView, PageMetaData):
    def get_queryset(self):
        pk = self.kwargs["pk"]
        return (
            self.model.published.select_related("category")
            .filter(category__pk=pk)
            .order_by("-modified_at")
        )

    def get_context_data(self, **kwargs):
        context = super(EntryByCategoryListView, self).get_context_data(**kwargs)

        try:
            category = "Category({0})".format(
                Category.objects.get(pk=self.kwargs["pk"]).name
            )
            context["title"] = category
        except Category.DoesNotExist:
            pass

        context["meta"] = self.get_meta(context=context)
        return context
