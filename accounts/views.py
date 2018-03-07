# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView

from django.contrib.auth.views import LoginView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from blog.models import Entry, Category


class UserLogin(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return resolve_url('dashboard')


@method_decorator(login_required, name='dispatch')
class DashBoard(DetailView):
    template_name = 'dashboard.html'
    context_object_name = 'user'
    model = get_user_model()

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(DashBoard, self).get_context_data(**kwargs)
        context['title'] = "Dashboard"
        context['categories'] = Category.objects.all().order_by("name")
        return context


@method_decorator(login_required, name='dispatch')
class DashBoardEntryListView(ListView):
    template_name = 'dashboard.html'
    context_object_name = 'entries'
    paginate_by = 12
    model = Entry

    def get_queryset(self):
        return self.model.objects.select_related("author")\
            .filter(author=self.request.user).order_by('-modified_at')


@method_decorator(login_required, name='dispatch')
class EditProfileView(UpdateView):
    model = get_user_model()
    fields = ('first_name', 'last_name')
    template_name = 'edit_profile.html'

    def get_success_url(self):
        return resolve_url('dashboard')
