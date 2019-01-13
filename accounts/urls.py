# -*- coding: utf-8 -*-
from django.urls import path, re_path

from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from accounts.views import DashBoard, DashBoardEntryListView, EditProfileView, UserLogin


urlpatterns = [
    path("dashboard/", DashBoard.as_view(), name="dashboard"),
    path(
        "dashboard/my-posts/",
        DashBoardEntryListView.as_view(),
        name="dashboard-entries",
    ),
    path(
        "dashboard/update-profile/<int:pk>/",
        EditProfileView.as_view(),
        name="update-profile",
    ),
    path("login/", UserLogin.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("login")), name="logout"),
    path(
        "password_change/",
        PasswordChangeView.as_view(template_name="password_change_form.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(template_name="password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(template_name="password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
