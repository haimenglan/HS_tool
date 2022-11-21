from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect
from django.http import JsonResponse

from HS_server.models import Book, Python_doc, English_doc, College_doc, Python_module
from login.models import Contact
from picture.models import Wallpaper

from HS_server_django import settings
import login
import os
import zipfile, re

def start(request):
    context_dict = login.views.get_userinfo_context(request)
    return render(request, "data_sync/data_sync.html", context=context_dict)

def delete_not_exists_book(table):
    '''
    删除数据库里无效文件
    '''
    book_l = table.objects.all()
    for b in book_l:
        # print(os.path.join(settings.STATIC_DIR, b.path))
        if not os.path.exists(os.path.join(settings.STATIC_DIR, b.path)):
            print('文件不存在', os.path.join(settings.STATIC_DIR, b.path))
            b.delete()


def delete_not_exists_file(request):
    delete_not_exists_book(Book)
    return return_update_result(request)


def add_book(book_path, table):
    if "\\" in book_path:
        book_path = book_path.replace("\\", "/")
    name = os.path.splitext(os.path.basename(book_path))[0] # 文档名
    if os.path.basename(book_path)=='index.html':  
        name = os.path.basename(os.path.dirname(book_path))
    path = book_path.replace(settings.STATIC_DIR+os.sep, '') # 文档保存在数据库的路径
    format_ = os.path.splitext(os.path.basename(book_path))[1]
    if not table.objects.filter(name=name).exists():
        # print('此书不存在', book_path)
        b = table()
    else:
        try:
            b = table.objects.filter(name=name).get()
        except:
            b = None
    if b is not None:
        b.name = name 
        b.path = path
        b.format = format_
        b.save()
        return name


def sync_book(book_dir, table, skip_dir = [], skip_path=[]):
    change_list = []
    for current_path, dirs, paths in os.walk(book_dir):
        is_skip = False
        for i in skip_dir: # 跳过skip_dir里面包含的文件夹及其包含的所有内容
            if i in current_path:
                is_skip = True
        if is_skip:
            continue
        if 'index.html' in paths: 
            skip_dir.append(current_path)
            book_path = os.path.join(current_path, 'index.html')
            add_book(book_path, table) # 添加HTML路径,跳过此当前路径的其它所有文件
            continue
        for path in paths:  # 添加当前路径下所有文件
            if "_index2.txt" in path or ".DS_Store" in path or \
                (os.path.splitext(path)[1]=='.html' and os.path.exists( # 如果是 word 转 html 生成的文件和索引，不添加html，只添加docx
                                os.path.join(current_path, os.path.splitext(path)[0]+'.docx'))):
                continue
            book_path = os.path.join(current_path, path)
            result = add_book(book_path, table)
            if result is not None:
                change_list.append(result)
    return change_list


def return_update_result(request, change_list=[]):
    context_dict = login.views.get_userinfo_context(request)
    context_dict['change_list'] = "new add: " + str(change_list)
    return render(request, "data_sync/result.html", context=context_dict)


def sync_note(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    change_list = sync_book(path, Book)
    return return_update_result(request, change_list)

def sync_note_in_zip(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    note = zipfile.ZipFile(path)
    skip_list = []
    for i in note.namelist():
        is_skip = False
        for j in skip_list: # 跳过EPUB文件包除了epub根目录的其它文件
            if j in i:
                is_skip = True
        if not is_skip and i!='note/' and i!='note/.DS_Store':
            if ".epub" in i:
                book_name = re.search(".+?\.epub", i).group()
                skip_list.append(book_name)
                add_book("HS_server/"+book_name, Book)
                continue
            else:
                add_book("HS_server/"+i, Book)
    return return_update_result(request)

def add_book2zip(request):
    '''
        将note_new里面的书籍添加到note压缩包内部
    '''
    new_book_dir = os.path.join(settings.STATIC_DIR, 'HS_server/note_new')
    zip_dir = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    for i in os.listdir(new_book_dir):
        if '.DS_Store' not in i:
            book_path = os.path.join(new_book_dir, i)
            zip_f = zipfile.ZipFile(zip_dir, 'a')
            zip_f.write(book_path, arcname="note/" +os.path.basename(book_path))
            os.remove(book_path)
    return return_update_result(request)


def sync_python(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/document/python资料')
    skip_dir = [os.path.join(settings.STATIC_DIR, 
                             'HS_server/document/python/django课件/Django课件V3.1/其他'), 
                os.path.join(settings.STATIC_DIR, 
                             'HS_server/document/python/django课件/Django课件V3.1/FastDFS'), 
                os.path.join(settings.STATIC_DIR, 
                             'HS_server/document/python/前端html-css-javascript-jquery课件/jqueryApi'), 
                os.path.join(settings.STATIC_DIR, 
                             'HS_server/document/python/django课件/Django课件V3.1/goods'),
               ]
    sync_book(path, Python_doc, skip_dir)
    return return_update_result(request)

def sync_english(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/document/English')
    sync_book(path, English_doc)
    return return_update_result(request)

def sync_college(request):
    print("同步大学课程")
    path = os.path.join(settings.STATIC_DIR, 'HS_server/document/大学课程')
    sync_book(path, College_doc)
    return return_update_result(request)

def sync_wallpaper(request):
    path = os.path.join(settings.STATIC_DIR, 'wallpapers')
    sync_book(path, Wallpaper, skip_path=["Thumbnail", ".DS_Store"])
    return return_update_result(request)
 



