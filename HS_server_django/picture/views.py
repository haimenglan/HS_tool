from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect
from django.http import JsonResponse
from picture.models import Wallpaper 
from HS_server_django import settings
import login
import os
import PIL

def change_photo_size(file_path, save_path, width, is_zoomout=False, is_square=False, height=None):
    try:
        image = PIL.Image.open(file_path)
        image_size = image.size  # (宽，高)
        if width < image_size[0] or is_zoomout:  # 小的图片不放大，除非指定is_zoomout为True
            if height is not None:
                image_size = (width, height)
            else:
                image_size = (width, int(image_size[1] / image_size[0] * width))
        if is_square:
            image_size = (image_size[0], image_size[0])
        image = image.resize(image_size)
        image.save(save_path)
    except Exception as e:
        # print(str(e))
        pass

def index(request):
    context_dict = login.views.get_userinfo_context(request)
    img_list = Wallpaper.objects.all()
    img_list_new = []
    for i in img_list:
        img_dir = os.path.dirname(i.path)
        img_name = os.path.basename(i.path)
        Thumbnail_name = os.path.splitext(img_name)[0]+"_Thumbnail"+os.path.splitext(img_name)[1]
        Thumbnail_path = os.path.join(img_dir, Thumbnail_name)
        if not os.path.exists(os.path.join(settings.STATIC_DIR,Thumbnail_path)):
            change_photo_size(os.path.join(settings.STATIC_DIR, i.path), 
                                os.path.join(settings.STATIC_DIR,Thumbnail_path), 600, height=400)
        img_list_new.append({"name": img_name, "path": Thumbnail_path,"id":i.id})
    context_dict["img_list"] = img_list_new
    print(context_dict)
    return render(request, "picture/picture.html", context=context_dict)

def img_detail(request, id):
    # print("id is ", id)
    try:
        context_dict = login.views.get_userinfo_context(request)
        image = Wallpaper.objects.filter(id=id).get()
        print("image is ", image)
        context_dict["img"] = image
        return render(request, "picture/picture_detail.html", context=context_dict)
    except Exception as e:
        return HttpResponse(str(e))

def add_image(request):
    # path = "/Users/js-15400155/Desktop/python/HS_tool/HSTool4.1/HS_server_django_symple/static/wallpapers"
    # for i in os.listdir(path):
    #     is_exist = Wallpaper.objects.filter(name=i.split(".")[0]).exists()
    #     print(f"添加{i}")
    #     if is_exist:
    #         print(i, "已存在")
    #         # b = Wallpaper.objects.filter(name=i.split(".")[0]).get()  
    #     else:
    #         if ".DS_Store" not in i:
    #             b = Wallpaper()
    #             b.name = i.split(".")[0]
    #             b.path = os.path.join("wallpapers", i)
    #             b.img_format = os.path.splitext(i)[1]
    #             b.img_type = "wallpaper"
    #             b.save()
    return HttpResponse("finished")