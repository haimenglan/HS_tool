from django.urls import path
from django.urls import re_path
from OPP import views

urlpatterns = [
   re_path(r"^$", views.start),
   re_path(r"^submit_csvfile$", views.submit_csvfile),
   re_path(r"^generate_picture$", views.generate_picture),
]