from django.urls import path
from django.urls import re_path
from login import views

urlpatterns = [
   re_path(r"^$", views.login, name="login"),
   re_path(r"^click_login", views.click_login),
   re_path(r"^logout$", views.logout),
   re_path(r"^register$", views.register),
   re_path(r"^setting$", views.setting),
   re_path(r"^setting/submit$", views.setting_submit),
   re_path(r"^help$", views.help),
]
