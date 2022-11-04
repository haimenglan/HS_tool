
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect
from django.http import JsonResponse
import os, time, random
import sys
import json
import re
import base64
from urllib import parse
import zipfile
from io import BytesIO
import traceback
import tools.book
import log
import csv
# import logger as logger

MY_DIR = os.path.dirname(__file__)  # /Users/js-15400155/Desktop/HS_server_django/HS_server
sys.path.append(MY_DIR)
sys.path.append(os.path.join(MY_DIR, "modules"))

from tools import UnitdetailsDataTool, compare_overlay_FOMs
from HS_server.models import Book, Python_doc, Python_module, \
Health_Sensing_doc, English_doc, HWTE_Station_doc
from login.models import Contact

G_STATIC_PATH = os.path.join(os.path.dirname(MY_DIR),"static")
from django.conf import settings
daily_down_load_dir = os.path.join(settings.MEDIA_ROOT, "Daily")
FOM_down_load_dir = os.path.join(settings.MEDIA_ROOT, "FOM")
import login.views
from login.views import login_check

# 视图中的路径都是模板下的路径
def create_log():
        # 第一步，创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级总开关
    # logfile = '/Users/js-15400155/Desktop/log.txt'
    logfile = os.path.join(os.path.dirname(__file__), 'log.txt')
    if not os.path.exists(logfile):
        with open(logfile, "w", encoding="utf8") as f:
            try:
                f.write("文件不存在，重新创建")
                f.close()
            except Exception as e:
                f.write(str(e))
                f.close()
    fh = logging.FileHandler(logfile, mode='a')  # open的打开模式这里可以进行参考
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)   # 输出到console的log等级的开关

    # 第四步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 第五步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)

    # 日志总开关
    # logger.disabled = True
    return logger

# import log
import logging
logger = create_log()

# 视图中的路径都是模板下的路径

def index(request):
    # 返回模板templates下的HS_server/index.html文件
    addr = request.get_full_path()
    logger.info(f"地址是{addr}")
    if "favicon.ico" in str(addr):
        logger.info(f'获取favicon.ico')
        return HttpResponse("就是不给你")
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 访问主页 +++++++++++\n')

    context_dict = {"user_name": "无名", "user_sign": "请让我独享经验", "login_button":"登录", "login_link": "/login" }
    session = request.session.get("user_account")
    if session:
        user = Contact.objects.filter(account=session).get()
        context_dict["login_button"] = f"退出"
        context_dict["login_link"] = "/login/logout"
        context_dict["user_name"] = user.name
        context_dict["user_sign"] = user.sign
    result = render(request, "HS_server/index.html", context=context_dict)
    return result

# frameset 方法显示主页内容
# def topframe(request):
    # context_dict = {}
    # result = render(request, "HS_server/top.html", context=context_dict)
    # return result
#
# def leftframe(request):
    # context_dict = {"tool_list": "工具列表"}
    # return render(request, "HS_server/left.html", context=context_dict)
#
# def rightframe(request):
    # context_dict = {}
    # return render(request, "HS_server/right.html", context=context_dict)
#
# def mainframe(request):
    # context_dict = {}
    # return render(request, "HS_server/main.html", context=context_dict)

def save_file(path, fObj):
    with open(path, "wb") as f:
        for item in fObj.chunks():
            f.write(item)

def generate_file_name(name):
    return f'{int(time.time())}{random.randint(1000, 6000)}{name}'

def daily_report_tool(request):
    '''
    1. 获取模式参数
    2. 获取原始数据文件内容并保存
    3. 运行daily_report_tool并转化成html
    '''
    try:
        logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 运行daily +++++++++++\n')
        if request.method == 'POST':
            # 获取模式参数
            mode_dict = {"show empty":0, "change config":0, "is FBR config":0, "is platinum":0}
            for each_key in mode_dict:
                if request.POST.get(each_key) is not None:
                    mode_dict[each_key] = 1
            # 获取原始数据文件
            unitdetails_file = request.FILES.get("unitdetails_file")
            # print("daily提交的数据 ++++++++++", request.POST, request.FILES)
            if unitdetails_file is not None:
                # 保存原始数据文件
                file_name = generate_file_name(unitdetails_file.name)
                if not os.path.exists(daily_down_load_dir):
                    os.mkdir(daily_down_load_dir)
                download_path = os.path.join(daily_down_load_dir, file_name)
                save_file(download_path, unitdetails_file)
                # 运行daily_report_tool
                unitdetailsData = UnitdetailsDataTool.UnitdetailsData(download_path, mode_dict["show empty"],
                                                                    mode_dict["change config"], mode_dict["is FBR config"],
                                                                    is_platinum=mode_dict["is platinum"])
                # 处理运行结果
                save_name = os.path.splitext(os.path.basename(download_path))[0]+"_result.xls" # 保存文件名字
                xls_path = os.path.join(os.path.dirname(download_path), save_name) # 保存文件路径
                unitdetails_xls = UnitdetailsDataTool.Unitdetails_xls(xls_path, unitdetailsData) # 生成表格文件
                # 将结果转换成html
                option_button = "" # 每个sheet对应一个按钮
                option_result = "" # 每个按钮对应一张sheet内容
                for i, sheet_name in enumerate(unitdetails_xls.html_xls.sheet_name_list):
                    if i==0:
                        option_button += f'<li class="current_option"> {sheet_name} </li>'
                    else:
                        option_button += f'<li> {sheet_name} </li>'
                    option_result += unitdetails_xls.html_xls.xls[sheet_name]
                # 渲染模板
                context = {"option_button":option_button, "option_result":option_result, "file_name":save_name}
                os.remove(download_path) # 删除下载的原始数据
                return render(request, "HS_server/mainframes/daily_result.html", context=context)
    except Exception as e:
        return HttpResponse("运行失败"+str(e))


def download_daily_result(request):
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 下载daily +++++++++++\n')
    try:
        file_name = request.GET.get('file_name')
        download_path = os.path.join(daily_down_load_dir, file_name)
        if os.path.exists(download_path):
            with open(download_path, "rb") as f:
                result = f.read()
            os.remove(download_path)
            return HttpResponse(result)
    except:
        return HttpResponse("下载失败，文件不存在或者已删除, 请重新运行")


def FOM_compare_tool(request):
    '''
    1. 获取新&旧版本原始数据文件并保存
    2. 运行对比工具并返回结果
    '''
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 运行FOMs对比 +++++++++++\n')
    if request.method == 'POST':
        try:
            # print("开始对比")
            old_file = request.FILES.get("old_version_file")
            old_file_name = generate_file_name(old_file.name)
            if not os.path.exists(FOM_down_load_dir):
                os.mkdir(FOM_down_load_dir)
            old_path = os.path.join(FOM_down_load_dir, old_file_name)
            save_file(old_path, old_file)
            new_file = request.FILES.get("new_version_file")
            new_file_name = generate_file_name(new_file.name)
            new_path = os.path.join(FOM_down_load_dir, new_file_name)
            save_file(new_path, new_file)

            result_path = os.path.dirname(old_path)
            result_xls = compare_overlay_FOMs.main(old_path, new_path, result_path)
            download_name = os.path.basename(result_xls.save_path)
            # 生成下载链接

            result = f'<div class="download"> \
                        <a href="download_compare_FOMs_result?file_name={download_name}" download="{download_name}">下载结果</a> \
                    </div>'
            # 生成html运行结果
            # print("对比结果+++++++++++",result_xls.html_xls.sheet_name_list)
            for each_sheet in result_xls.html_xls.sheet_name_list:
                result += result_xls.html_xls.xls[each_sheet]
            os.remove(old_path)
            os.remove(new_path)
            return HttpResponse(result)
        except Exception as e:
            # traceback.print_exc()
            # print(str(e))
            return HttpResponse("对比失败, 请检查上传文件及其数据是否正确")


def download_compare_FOMs_result(request):
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 下载FOMs对比 +++++++++++\n')
    try:
        file_name = request.GET.get('file_name')
        download_path = os.path.join(FOM_down_load_dir, file_name)
        if os.path.exists(download_path):
            with open(download_path, "rb") as f:
                result = f.read()
            return HttpResponse(result)
    except:
        return HttpResponse("下载失败，文件不存在，可能已被删除")


@login_check
def book_tool(request):
    '''
    查找小说列表, 返回第page页的num部小说， 如果是第一页返回小说总数量（用来生成页码）
    '''
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 查看小说列表 +++++++++++\n')
    page = int(request.GET.get("page"))
    num = int(request.GET.get("num"))
    response_dict = {"book_name_list":[], "book_id_list":[], "format_list": [], "book_total": 0}
    start = (page-1)*num
    end = page*num
    result = Book.objects.all()[start:end]
    if page==1:
        book_total = Book.objects.count()
        response_dict["book_total"] = book_total
    for each_book in result:
        response_dict["book_id_list"].append(each_book.id)
        response_dict["book_name_list"].append(each_book.name)
        response_dict["format_list"].append(each_book.format)
    return HttpResponse(json.dumps(response_dict))


def is_zip(path):
    '''
    判断path是可以直接读取的文件，还是放在一个压缩文件里面的文件
    '''
    if os.path.exists(path):
        return ""
    else:
        while path:
            path = os.path.dirname(path)
            if os.path.exists(path):
                return path
        return ""

def get_book_table(bookTable):
    result = Book
    if bookTable == "python_doc":
        result = Python_doc
    elif bookTable == "health_sensing":
        result = Health_Sensing_doc
    elif bookTable == "english":
        result = English_doc
    elif bookTable == "HWTE_Station":
        result = HWTE_Station_doc
    return result


@login_check
def get_book_content(request):
    '''
    返回ID为book_ID的书籍第page页的内容或者页码
    '''
    book_table = get_book_table(request.GET.get("bookTable"))
    book_ID = request.GET.get("bookID")
    page = request.GET.get("page")
    request_type = request.GET.get("request")
    print('requst type is', request_type)
    try:
        b = book_table.objects.filter(id=book_ID).get()
        if b.format == ".pdf":
            link = f"/static/pdfjs-dist/web/viewer.html?file=../../" + f"{b.path}"  # 直接让它访问静态文件
            return HttpResponse(json.dumps({"file_type": "pdf", "data": "", "link": link}))
        elif b.format == ".html":  # print("收到获取课件事件",target_doc_path)
            # 方法一 手动返回html文件，这样必须定义一个视图函数，手动返回html中用到的css，js等静态文件（因为这个html引用的文件并没有load static）
            # 方法二 重定向, 但是浏览器是Ajax访问的，重定向不可用
            # return HttpResponseRedirect(f"/static/{target_doc.path}")
            # 方法三 返回链接，让浏览器访问静态html文件
            return HttpResponse(json.dumps({"file_type": "html", "data": "", "link": f"/static/{b.path}"}))
        elif b.format == ".pptx":  # 因为无法转换ppt，暂时手动转成pdf文档
            path = b.path.replace(".pptx", '.pdf')
            link = f"/static/pdfjs-dist/web/viewer.html?file=../../" + f"{path}"
            # print("链接是", link)
            return HttpResponse(json.dumps({"file_type": "pdf", "data": "", "link": link}))

        book_path = os.path.join(G_STATIC_PATH, b.path)
        logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 阅读{b.name} +++++++++++\n')
        # print(f" ++++++++++ 阅读{b.name} +++++++++++")
        zip_path = is_zip(book_path)
        book = tools.book.Book(book_path, zip_path=zip_path)
        if request_type == "content":
            book_content = book.get_chapter(int(page))
            response_dict = {"book_content": book_content, "file_type": b.format}
        elif request_type == "page_num":
            print('page num is', book.page_num)
            response_dict = {"page_num": book.page_num}
        elif request_type == "index":
            response_dict = {"index": book.get_index()}
        return JsonResponse(response_dict)
    except Exception as e:
        traceback.print_exc()
        response_dict = {"book_content": f"找不到此书籍"+str(e)}
        return HttpResponse(json.dumps(response_dict))

def get_book_image(request, book_table, book_ID, image_path):
    '''
        返回书籍中需要的静态文件
    '''
    book_table = get_book_table(book_table)
    b = book_table.objects.filter(id=book_ID).get()
    book_path = os.path.join(G_STATIC_PATH, b.path)
    zip_path = is_zip(book_path)
    book = tools.book.Book(book_path, zip_path=zip_path)
    f = book.get_static_file(image_path)
    response =  FileResponse(f)
    if ".css" in image_path:
        response['Content-Type'] = 'text/css'
        return HttpResponse("不用它的样式")
    elif ".js" in image_path:
        response['Content-Type'] = 'text/javascript'
    # 方法二 手动读取返回
    # path = os.path.join(G_STATIC_PATH, path)
    # if os.path.exists(path):
    # with open(path, "r") as f:
    # data = f.read()
    # return HttpResponse(data)
    return response

def download_verify(request, book_table, book_ID):
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 申请下载书籍 +++++++++++\n')
    bookID = request.GET.get("bookID")
    password = request.GET.get("password")
    if password == "3Q!":
        result = 1
        table = get_book_table(book_table)
        b = table.objects.filter(id=bookID).get()
        book_path = os.path.join(G_STATIC_PATH, b.path)
        book_path = parse.quote(base64.b64encode(book_path.encode()).decode())  # url编码发给浏览器，防止浏览器请求这个链接时，服务器收到的参数不对
        # todo 每天更新下载链接
        link = f"downloadLink?book_path={book_path}"
    else:
        result = 0
        link = ""
    return HttpResponse(json.dumps({"result": result, "link": link}))

def download_book(request):
    '''
    '''
    book_path = request.GET.get("book_path") # url发送过来会自动url解码
    book_path = base64.b64decode(book_path).decode() # 书籍的完整路径 /desktop/xxx/note/诛仙.epub
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 下载小说{os.path.basename(book_path)} +++++++++++\n')
    zip_path = is_zip(book_path)
    book = tools.book.Book(book_path, zip_path=zip_path)
    data = book.download()
    download_filename = os.path.basename(book_path)
    response = HttpResponse(data, headers={'Content-Type': 'application', # 告诉浏览器以附件打开此内容
                                         'Content-Disposition': # 告诉浏览器下载文件的名字
                                             f'attachment; filename="{download_filename}"'.encode() # utf编码让浏览器识别中文
                            })
    return response

@login_check
def python_doc(request, parent=None):
    '''
    1. 从数据库获取资料列表, 并在模板中显示
    2. 模板中定义点击资料名称事件， ajax发送请求获取对应资料内容
    3. 模板中显示资料内容并生成目录
    '''
    logger.info(f'{request.META["REMOTE_ADDR"]} ++++++++++ 查看python列表 +++++++++++\n')
    doc_list = Python_doc.objects.all().order_by("order_id")
    module_list = Python_module.objects.all().order_by("-order_id")
    # health_sensing_list = Health_Sensing_doc.objects.all().order_by("-order_id")
    context_dict = login.views.get_userinfo_context(request)
    context_dict.update({"doc_list": doc_list, "module_list":module_list})
    result = render(request, "HS_server/python_doc.html", context=context_dict)
    return result

def get_python_doc_list(request):
    doc_type = request.GET.get("doc_type")
    doc_obj = get_book_table(doc_type)
    doc_all = doc_obj.objects.all().order_by("order_id")
    doc_list = [i.name+i.format for i in doc_all ]
    doc_id = [i.id for i in doc_all]
    return JsonResponse({"doc_list":doc_list, "doc_id":doc_id})

def get_python_doc_download_module(request):
    try:
        id = request.GET.get('id')
        module = Python_module.objects.filter(id=id).get()
        logger.info(
            f'{request.META["REMOTE_ADDR"]} ++++++++++ 下载python模块{module.name} +++++++++++\n')
        module_path = os.path.join(G_STATIC_PATH, module.path)
        print("下载模块", module_path)
        if os.path.exists(module_path):
            with open(module_path, "rb") as f:
                result = f.read()
            return HttpResponse(result, headers={'Content-Type': 'application', # 告诉浏览器以附件打开此内容
                                             'Content-Disposition': # 告诉浏览器下载文件的名字
                                                 f'attachment; filename="{module.name}{module.format}"'.encode() # utf编码让浏览器识别中文
                                })
        else:
            return HttpResponse("文件不存在")
    except Exception as e:
        # print("下载模块出错了", str(e))
        return HttpResponse("下载失败，文件不存在，可能已被删除")
























def write_csv(save_path, list):
    with open(save_path, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        for each in list:
            csv_writer.writerow(each)
        f.close()

def read_csv(file_path):
    with open(file_path, "r", encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        return [each_line for each_line in csv_reader]

def export_sql_csv2(table, field, save_path):
    book = table.objects.all()
    book_list = [field]
    for each_book in book:
        line = []
        for each_field in field:
            if each_field == "name":
                line.append(each_book.name)
            if each_field == "path":
                line.append(each_book.path)
            if each_field == "format":
                line.append(each_book.format)
            if each_field == "author":
                line.append(each_book.author)
        book_list.append(line)
    write_csv(save_path, book_list)


def export_sql_csv(request):
    # obj = Contact.objects.all()
    # export_sql_csv2(Book, ["name", "author", "path", "format"],
                        # "/Users/js-15400155/Desktop/Health_Sensing_doc.csv")
    return HttpResponse("xxx hahaha")


def load_csv_sql2(csv_path, table):
    b_list = read_csv(csv_path)
    filed = b_list[0]
    # print(filed)
    for i in b_list[1:]:
        try:
            book = table.objects.filter(name=i[0]).get()
            # print("skip ", book)
        except:
            book = table()
            for j, k in enumerate(filed):
                if k=="name":
                    book.name = i[j]
                if k=="author":
                    book.author = i[j]
                if k=="path":
                    book.path = i[j]
                if k=="format":
                    book.format = i[j]
            book.save()
            # print("添加完成", book)

def load_csv_sql(request):
    # csv_dir = os.path.join(G_STATIC_PATH, "SQLdata_list")
    # csv_path = os.path.join(csv_dir, 'Python_module.csv')
    # load_csv_sql2(csv_path, Python_module)
    return HttpResponse("finished")


# 将图书添加到数据库
def add_doc(request):
    # doc_path = "/Users/js-15400155/Desktop/python/HS_tool/HSTool4.1/HS_server_django_symple/static/HS_server/python_doc/HWTE"
    # for each_doc in os.listdir(doc_path):
    #     is_exist_book = HWTE_Station_doc.objects.filter(name=each_doc).exists()
    #     print(f"添加{each_doc}")
    #     # print(f"检查书籍{book_name}是否存在，结果是{is_exist_book}")
    #     if is_exist_book:
    #         print("此书已存在", each_doc)
    #     else:
    #         if ".DS_Store" not in each_doc:
    #             b = HWTE_Station_doc()
    #             b.name = each_doc.split(".pdf")[0]
    #             b.path = os.path.join("HS_server/python_doc/HWTE", each_doc)
    #             b.format = os.path.splitext(each_doc)[1]
    #             b.save()
    return HttpResponse("finished")