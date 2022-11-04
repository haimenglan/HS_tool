"""HS_server_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.conf.urls import include
from HS_server import views
from OPP import views

urlpatterns = [
    re_path('admin/', admin.site.urls),
    # path(r"", views.index, name="index"),
    # 把 HS_server 开头的url 交给 HS_server 模块的urls.py处理
    re_path(r"^HS_server/", include("HS_server.urls")),
    re_path(r"^login/", include("login.urls")),
    re_path(r"^favicon.ico.?", include("HS_server.urls")),
    re_path(r"^OPP/", include("OPP.urls")),
    re_path(r"^picture/", include("picture.urls")),
    re_path(r"^help/", include("help.urls")),
    re_path(r"^data_update/", include("data_update.urls")),
]
