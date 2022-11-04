from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect
from django.http import JsonResponse

from HS_server_django import settings
import login
import os

def help(request):
    context_dict = login.views.get_userinfo_context(request)
    return render(request, "help/help.html", context=context_dict)