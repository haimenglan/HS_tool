from django.urls import path
from django.urls import re_path
from picture import views

urlpatterns = [
    re_path(r"^$", views.index),
    re_path(r"^add_image$", views.add_image),
    re_path(r"^show_detail/(\d+?)$", views.img_detail),
]