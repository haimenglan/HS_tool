from django.urls import path
from django.urls import re_path
from data_update import views

urlpatterns = [
    re_path(r"^$", views.start),
    re_path(r"^add_book2zip$", views.add_book2zip),
    re_path(r"^sync_note$", views.sync_note),
    re_path(r"^sync_note_in_zip$", views.sync_note_in_zip),
    re_path(r"^sync_python$", views.sync_python),
    re_path(r"^sync_english$", views.sync_english),
    re_path(r"^sync_hardware$", views.sync_hardware),
    re_path(r"^delete_not_exists_file$", views.delete_not_exists_file),
    re_path(r"^sync_wallpaper$", views.sync_wallpaper),
]