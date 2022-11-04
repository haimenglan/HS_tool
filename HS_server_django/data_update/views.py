
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect
from django.http import JsonResponse

from HS_server.models import Book, Python_doc, English_doc, Hardware_doc, \
Health_Sensing_doc, HWTE_Station_doc, Python_module
from login.models import Contact
from picture.models import Wallpaper

from HS_server_django import settings
import login
import os
import zipfile, re

def start(request): 
    context_dict = login.views.get_userinfo_context(request)
    return render(request, "data_sync/data_sync.html", context=context_dict)

def return_update_result(request, change_list=''):
    context_dict = login.views.get_userinfo_context(request)
    context_dict['change_list'] = change_list
    return render(request, "data_sync/result.html", context=context_dict)

def add_book(book_path, table):
    if os.sep=='\\':
        book_path = book_path.replace(os.sep, '/')
    name = os.path.splitext(os.path.basename(book_path))[0]
    if os.path.basename(book_path)=='index.html':  
        name = os.path.basename(os.path.dirname(book_path))
    if not table.objects.filter(name=name).exists():
        # print('此书不存在', book_path)
        b = table()
        b.name = name 
        b.path = book_path.replace(settings.STATIC_DIR+os.sep, '')
        b.format = os.path.splitext(os.path.basename(book_path))[1]
        b.save()
    else:
        # print('此书已存在', book_path)
        try:
            b = table.objects.filter(name=name).get()
            if b.path != book_path.replace(settings.STATIC_DIR+os.sep, ''):
                print('修改路径',b.name, b.path,  book_path)
                b.path = book_path.replace(settings.STATIC_DIR+os.sep, '')
                b.format = os.path.splitext(os.path.basename(book_path))[1]
                b.save()
                # print('保存')
        except:
            print('修改文件出错', name)
        
def sync_book(book_dir, table, skip_dir = [], skip_path=[]):
    for current_path, dirs, paths in os.walk(book_dir):
        is_skip = False
        for i in skip_dir:  # 如果当前路径是在skip文件夹下面则跳过循环
            if i in current_path:
                is_skip = True
                break
        if not is_skip:
            # todo word 转 html生成的文件夹也跳过
            # 如果是HTML项目文件夹，只添加.html文件，其余文件跳过
            if 'index.html' in paths: 
                skip_dir.append(current_path)
                book_path = os.path.join(current_path, 'index.html')
                add_book(book_path, table)# 添加HTML路径
                continue
            for path in paths:  # 添加当前路径下所有文件
                book_path = os.path.join(current_path, path)
                # 如果是 word 转 html 生成的文件和索引
                if "_index2.txt" in book_path:
                    continue
                is_skip = False
                for j in skip_path:
                    if j in book_path:
                        print("skip", j)
                        is_skip = True
                        break
                if os.path.splitext(book_path)[1]=='.html':
                    # print('当前文件为html, 不添加', book_path)
                    docx_name = os.path.splitext(path)[0]
                    docx_path = os.path.join(os.path.dirname(book_path), docx_name+'.docx')
                    # print('path', docx_path)
                    if os.path.exists(docx_path):
                        continue
                if not is_skip:
                    add_book(book_path, table)
                
def sync_note(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    sync_book(path, Book)
    return return_update_result(request)

def sync_note_in_zip(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    note = zipfile.ZipFile(path)
    skip_list = []
    for i in note.namelist():
        is_skip = False
        for j in skip_list:
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
    
def add_book2zip_(book_path, zip_path, mode='a'):
    zip_f = zipfile.ZipFile(zip_path, mode)
    zip_f.write(book_path, arcname="note/" +os.path.basename(book_path))

def add_book2zip(request):
    new_book_dir = os.path.join(settings.STATIC_DIR, 'HS_server/note_new')
    zip_dir = os.path.join(settings.STATIC_DIR, 'HS_server/note')
    for i in os.listdir(new_book_dir):
        if '.DS_Store' not in i:
            book_path = os.path.join(new_book_dir, i)
            add_book2zip_(book_path, zip_dir)
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

def sync_hardware(request):
    path = os.path.join(settings.STATIC_DIR, 'HS_server/document/硬件')
    sync_book(path, Hardware_doc)
    return return_update_result(request)

def sync_wallpaper(request):
    path = os.path.join(settings.STATIC_DIR, 'picture/wallpaper')
    sync_book(path, Wallpaper, skip_path=["Thumbnail", ".DS_Store"])
    return return_update_result(request)
 
 
def delete_not_exists_book(table):
    book_l = table.objects.all()
    for b in book_l:
        # print(os.path.join(settings.STATIC_DIR, b.path))
        if not os.path.exists(os.path.join(settings.STATIC_DIR, b.path)):
            print('文件不存在', os.path.join(settings.STATIC_DIR, b.path))

def delete_not_exists_file(request):
    # delete_not_exists_book(Book)
    return return_update_result(request)






    
