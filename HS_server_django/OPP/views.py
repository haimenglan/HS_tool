from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.http import JsonResponse
import login.views
from login.models import Contact
# Create your views here.
import os, csv
import uuid
import sys
MY_DIR = os.path.dirname(__file__) 
sys.path.append(MY_DIR)

import OPP.OPP_GRR as OPP_GRR
from OPP_GRR import CSV2pd
import base64
import traceback
import time
from django.conf import settings
down_load_dir = os.path.join(settings.MEDIA_ROOT, "OPP")

def start(request):
    context_dict = login.views.get_userinfo_context(request)
    context_dict["file_path"] = "file path"
    return render(request, "OPP/data_analysis.html", context_dict)

def submit_csvfile(request):
    '''
    接收文件数据读取item，factor
    保存文件到本地，记录文件名
    返回
    '''
    try:
        context_dict = login.views.get_userinfo_context(request)
        file_data = request.FILES.get("insight_csv_file")
        if not file_data:
            return redirect("/OPP")

        if not os.path.exists(down_load_dir):
            os.mkdir(down_load_dir)
        save_file_path = os.path.join(down_load_dir, str(uuid.uuid4())+".csv")
        with open(save_file_path,"wb") as f:
            for item in file_data.chunks():
                f.write(item)

        # csv2pd = CSV2pd(file_data)
        csv2pd = CSV2pd(save_file_path)
        context_dict["factor_list"] = csv2pd.factor_list
        context_dict["item_list"] = csv2pd.item_list
        context_dict["first_item"] = context_dict["item_list"][0]
        context_dict["file_path"] = os.path.basename(request.POST.get("file_path"))

        context_dict["response_file_name"] = os.path.basename(save_file_path)
        return render(request, "OPP/data_analysis.html", context_dict)
    except Exception as e:
        # return redirect("/OPP")
        print("运行错误",str(e))
        traceback.print_exc()
        return HttpResponse(f"running error: {str(e)}")

def generate_picture(request):
    item = request.POST.get("item").strip(" ")
    image_type = request.POST.get("image_type").strip(" ")
    image_highlight = request.POST.get("image_highlight")
    image_highlight = "" if image_highlight is None else image_highlight.strip(" ")

    factor = request.POST.get("factor")
    factor_list = factor.split(";")
    factor_list = list({}.fromkeys([i.strip(" ") for i in factor_list]).keys())  # 去除空格，去除重复值，保留原有顺序
    file_name = request.POST.get("file_name").strip(" ")
    # print("收到ajax请求"+"*"*100, file_name, item, factor_list)
    path = os.path.join(down_load_dir, file_name)
    if os.path.exists(path):
        picture_bit_data = OPP_GRR.main(path, item, factor_list, image_type, image_highlight)
        if picture_bit_data=="factor too large":
            return JsonResponse({"result":False, "info":"factor too large"})
        bs64data = base64.encodebytes(picture_bit_data).decode()
        src = "data:image/png;base64,"+str(bs64data)
        return JsonResponse({"result":True, "src": src})
    else: 
        print("找不到文件")
        return JsonResponse({"result":False, "info":"找不到文件"})
