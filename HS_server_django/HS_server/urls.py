from django.urls import path
from django.urls import re_path
from HS_server import views

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"daily_report.py", views.daily_report_tool),
    re_path(r"download_daily_result", views.download_daily_result),
    re_path(r"FOM_compare.py", views.FOM_compare_tool),
    re_path(r"download_compare_FOMs_result", views.download_compare_FOMs_result),

    re_path(r"note.py", views.book_tool),
    re_path(r"note/[^/]+?/$", views.index),  # 刷新页面
    re_path(r"note/[^/]+?/content.py", views.get_book_content),
    re_path(r"note/[^/]+?/get_book_page.py", views.get_book_content),
    re_path(r"(note)/(\d+?)/downloadVerify.py", views.download_verify),
    re_path(r"note/[^/]+?/downloadLink.*", views.download_book),  # downloadLink
    re_path(r"(note)/(\d+?)/(.+)", views.get_book_image),

    re_path(r"^document/$", views.python_doc),
    re_path(r"^document/.*get_doc_list$", views.get_python_doc_list), # 这个的优先级大于下面的
    re_path(r"^document/.*/get_content.py", views.get_book_content),
    re_path(r"^document/.*/get_index.py", views.get_book_content),
    re_path(r"^document/.*download_module", views.get_python_doc_download_module), # 这个的优先级大于下面的
    re_path(r"^document/([^/]+)/(\d+)/[^/]+/(.+)", views.get_book_image),# 获取图片
    re_path(r"^document/[^/]+/\d+/[^/]+/", views.python_doc), # 刷新页面
]