from django.urls import path
from django.urls import re_path
from help import views

urlpatterns = [
    re_path(r"^$", views.help),
]