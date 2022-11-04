import zipfile
import re
import os
import hashlib
# import xml.sax as sax
# import xml.etree.ElementTree as ET
# from io import StringIO
from io import BytesIO
# import docx
import mammoth, base64
from bs4 import BeautifulSoup
import time
import shutil
import pickle

'''
本工具所有的电子书统一打包压缩存放在/Users/15400155/Desktop/xxx/HS_server/note下，note就是打包好的压缩文件
'''
G_encode_list = ["utf8", "gbk", "GB2312", "BIG", "big5", "GB18030", "Unicode", "utf16"]
def change2md5(string):
    '''
    把string转换成md5码
    '''
    md5 = hashlib.md5()
    md5.update(string.encode())
    return md5.hexdigest()

class Epub:
    def __init__(self, file_path):
        '''
        epub 文件其实是一个压缩包，里面有一个META-INF文件夹，这个文件夹下面有一个container.xml的文件，这个文件保存的是OPF文件路径
        而OPF文件保存的是书本的目录，目录对应书本内容的路径
        '''
        self.file_path = file_path
        self.isdir = os.path.isdir(self.file_path)
        self.xml_content = self.get_container_xml()
        # print(self.xml_content)
        self.opf_path = self.get_opf_path(self.xml_content)
        print(self.opf_path)
        self.opf_content = self.get_opf_content(self.opf_path)
        # print(self.opf_content)
        self.get_chapter_list(self.opf_content)
        print(self.chapter_list)
        self.get_chapter_name_list(self.opf_content)
        # print(self.chapter_name_list)
        self.zip_name_list = self.get_zip_name_list()
        print(self.zip_name_list)

    def get_container_xml(self):
        if not self.isdir:
            f = zipfile.ZipFile(self.file_path)
            self.xml_content = f.read(f"META-INF/container.xml").decode()
        else:
            with open(os.path.join(self.file_path, f"META-INF/container.xml")) as f:
                self.xml_content = f.read()
        return self.xml_content

    def get_opf_path(self, xml_content):
        opf_path = re.search(r'<rootfile full-path=.(.+?). media-type', str(xml_content))
        return "" if opf_path is None else opf_path.group(1)

    def get_zip_name_list(self):
        result = []
        if not self.isdir:
            f = zipfile.ZipFile(self.file_path)
            return f.namelist()
        else:
            for root, dirs, paths in os.walk(self.file_path):
                for i in paths:
                    name = os.path.join(root, i).replace(self.file_path)
                    result.append(name)
            return result

    def get_content_by_name(self, name):
        # print("获取", name, self.file_path)
        if not self.isdir:
            f = zipfile.ZipFile(self.file_path)
            content = f.read(name)
            # print(self.content)
        else:
            # print(os.path.join(self.file_path, name))
            with open(os.path.join(self.file_path, name), "rb") as f:
                content = f.read()
        return content

    def get_opf_content(self, opf_path):
        if not self.isdir:
            f = zipfile.ZipFile(self.file_path)
            self.opf_content = f.read(opf_path).decode()
        else:
            with open(os.path.join(self.file_path, opf_path)) as f:
                self.opf_content = f.read()
        return self.opf_content

    def get_chapter_list(self, opf_content):
        # 获取OPF文件里面的目录所在框架内容，可以自己打开一个ofp文件看一下
        # print(opf_content)
        re_compile = re.compile(r"<manifest>(.+)</manifest>", re.DOTALL) # 让点匹配所有字符
        self.manifest = re.search(re_compile, str(opf_content))
        # print(self.manifest)
        if self.manifest is not None:
            self.manifest = self.manifest.group(1)
            # 获取章节列表
            # 正则匹配<item id="chapter7" href="chapter6.xhtml" media-type="application/xhtml+xml"/>\n
            # 路径可能是.html也可能是.xhtml
            self.chapter_list = re.findall(r'href="([^<]+?\.x?html)"', str(self.manifest))
            # 获取章节总数
            self.chapter_num = len(self.chapter_list)
            return self.chapter_list

    def get_chapter_name_list_(self, opf_content):
        # 获取OPF文件里面的目录所在框架内容，可以自己打开一个ofp文件看一下
        # print(opf_content)
        self.chapter_name_dict = {}
        re_compile = re.compile(r"<guide>(.+)</guide>", re.DOTALL) # 让点匹配所有字符
        self.guid = re.search(re_compile, str(opf_content))
        # print(self.guid)
        if self.guid is not None:
            self.guid = self.guid.group(1)
            # 获取章节列表
            # 正则匹配<item id="chapter7" href="chapter6.xhtml" media-type="application/xhtml+xml"/>\n
            # <reference type="text" title="第一章 冠词和one，a little／a few， this， that?"  href="chapter2.html"/>
            # 路径可能是.html也可能是.xhtml
            self.chapter_name_list = re.findall(r'title="([^<]+?)" +?href="([^<]+?\.x?html)"', str(self.guid))
            if not self.chapter_name_list:
                for i in self.chapter_list:
                    self.chapter_name_list.append((i,i))
            else:
                result = []
                for i in self.chapter_name_list:
                    result.append((i[1], i[0]))
                self.chapter_name_list = result

            for i in self.chapter_name_list:
                self.chapter_name_dict[i[0]] = i[1]
            return self.chapter_name_list

    def get_chapter_name_list(self, opf_content):
        self.chapter_name_list = []
        for i, chapter in enumerate(self.chapter_list):
            content = self.get_chapter(i)
            soup = BeautifulSoup(content, "lxml")
            alink = soup.find_all('a')
            if alink:
                for each_a in alink:
                    if "href" in each_a.attrs:
                        index0 = each_a.attrs["href"] if "#" not in each_a.attrs["href"] else each_a.attrs["href"].split("#")[0]
                        parent_path_list = chapter.split("/")[:-1]
                        parent_path = ""
                        for j in parent_path_list:
                            parent_path += j+"/"
                        index0 = parent_path+index0
                        index1 = each_a.get_text()
                        # print("index0 is", index0)
                        # print("index1 is", index1)
                        self.chapter_name_list.append((index0,index1))
        if not self.chapter_name_list:
            return self.get_chapter_name_list_(opf_content)
        return self.chapter_name_list


    def get_chapter(self, chapter_num):
        '''
        根据传入的第几章参数，获取对应章节所在文件的内容
        '''
        if chapter_num<=self.chapter_num and chapter_num>0:
            chapter_name = self.chapter_list[chapter_num-1]
            # chapter_path = os.path.join(os.path.dirname(self.opf_path), chapter_name)
            chapter_path = os.path.dirname(self.opf_path)+"/"+ chapter_name
            if not self.isdir:
                f = zipfile.ZipFile(self.file_path)
                return f.read(chapter_path).decode()
            else:
                with open(os.path.join(self.file_path, chapter_path)) as f:
                    return f.read()
        else:
            return "找不到章节内容"

# book = Epub("/Users/js-15400155/Desktop/英语常用词疑难用法手册-陈用仪.epub")


class EpubHS(Epub):
    def __init__(self, file_path, zip_path):
        '''
        file_path: "/Users/15400155/Desktop/xxx/HS_server/note/xxx/诛仙.epub"
        zip_path: "/Users/15400155/Desktop/xxx/HS_server/note"
        '''
        self.zip_f = zipfile.ZipFile(zip_path)
        self.file_path_in_zip = file_path.replace(os.path.dirname(zip_path)+os.sep, "") # note/xxx/诛仙.epub
        self.isdir, self.epub_zip_f = False, None
        try:
            # epub是文件夹
            self.xml_content = self.zip_f.read(f"{self.file_path_in_zip}{os.sep}META-INF{os.sep}container.xml").decode()
        except:
            # epub是压缩文件
            self.isdir = True
            epub_data = self.zip_f.read(self.file_path_in_zip)
            epub_f = BytesIO() # 创建类文件对象, 代替创建本地的压缩文件
            epub_f.write(epub_data)
            epub_f.seek(0)
            self.epub_zip_f = zipfile.ZipFile(epub_f)
            self.xml_content = self.epub_zip_f.read("META-INF/container.xml").decode()

        self.opf_path = self.get_opf_path(self.xml_content)
        self.opf_content = self.get_opf_content(self.opf_path)
        self.get_chapter_list(self.opf_content)
        self.get_chapter_name_list(self.opf_content)
        self.get_chapter(10)

    @property
    def zip_name_list(self):
        result = []
        if self.isdir:
            return self.epub_zip_f.namelist()
        else:
            for i in self.zip_f.namelist():
                if self.file_path_in_zip in i:
                    result.append(i)
            return result
            

    def get_content_by_name(self, name):
        if self.isdir:
            content = self.epub_zip_f.read(name)
        else:
            content = self.zip_f.read(name)
        return content

    def get_opf_content(self, opf_path):
        if self.isdir:
            self.opf_content = self.epub_zip_f.read(opf_path).decode()
        else:
            self.opf_content = self.zip_f.read(f"{self.file_path_in_zip}{os.sep}{opf_path}").decode()
        return self.opf_content

    def get_chapter(self, chapter_num):
        '''
        根据传入的第几章参数，获取对应章节所在文件的内容
        '''
        if chapter_num<=self.chapter_num and chapter_num>0:
            chapter_name = self.chapter_list[chapter_num-1]
            chapter_path = os.path.join(os.path.dirname(self.opf_path), chapter_name)
            if self.isdir:
                # print(self.epub_zip_f.read(chapter_path).decode())
                return self.epub_zip_f.read(chapter_path).decode()
            else:
                return self.zip_f.read(f"{self.file_path_in_zip}{os.sep}{chapter_path}").decode()
        else:
            return "找不到章节内容"

# EpubHS("/Users/js-15400155/Desktop/note/哈利波特完整系列.epub", "/Users/js-15400155/Desktop/note")
# e = Epub("/Users/js-15400155/Desktop/python/HS_tool/HSTool4.1/HS_server_django_symple/static/HS_server/python_doc/English/英语常用词疑难用法手册-陈用仪.epub")
# print(e.get_chapter(1))

class Txt:
    def __init__(self, file):
        """
        传入的参数file是压缩文件的txt文件完整路径：file = "/Users/15400155/Desktop/xxx/HS_server/note/诛仙.txt"
        """
        self.encode_check_list = ["utf8", "gbk", "GB2312", "BIG", "big5", "GB18030", "Unicode", "utf16"]
        self.file = file
        self.page_num = None
        self.page_length = 10000

    def content(self, page):
        if not os.path.exists(self.file):
            zip_path = re.search(".+?note", self.file)
            if zip_path is not None:
                return self.content_in_zip(page, zip_path.group())
            else:
                return "找不到章节内容".encode()
        else:
            return self.content_in_folder(page)

    def content_in_folder(self, page):
        """
        先读走(page-1)*10000个字符
        再读当前页10000个字符
        每次读取10000个字符，每次这一万字符都循环所有的编码读取，如果循环结束还读取不了，则返回失败
        意思是，前面的10000个字符可能utf8读取成功， 但是后面的10000个字符，用gbk才读取成功！！
        """
        current_tell = 0
        for i in range(page):
            for j, each_code_m in enumerate(self.encode_check_list):
                try:
                    f = open(self.file, encoding=each_code_m, mode="r")
                    f.seek(current_tell)
                    book_content = f.read(self.page_length) # 这一步失败直接跳转到except
                    current_tell = f.tell()  # 下次读取从这里开始
                    if i==page-1: #如果是当前页码
                        # print(f"第{i+1}页{each_code_m}解码成功，将返回内容")
                        if self.page_num is None:
                            f.seek(0)
                            self.page_num = len(f.read()) / 10000
                            self.page_num = int(self.page_num) + 1 if self.page_num > int(self.page_num) else int(
                                self.page_num)
                        f.close()
                        return book_content
                    # print(f"第{i+1}页用{each_code_m}解码成功")
                    break
                except:
                    if j==len(self.encode_check_list)-1:
                        return f"文件解码失败"
                    # print(f"{each_code_m}解码失败, 换一种解码方式读取")

    def content_in_zip(self, page, zip_path):
        """
        传入第几页，和note文件路径
        """
        f = zipfile.ZipFile(zip_path, "r")
        # 这是由于txt文件可能是放在note下面的文件夹里面，比如 "/Users/15400155/Desktop/xxx/HS_server/note/玄幻/诛仙.txt"
        book_path = self.file.replace(os.path.dirname(zip_path)+os.sep, "") # 抠出txt文件在note下的路径
        raw_content = f.read(book_path) # 从压缩文件读取txt内容
        for i in range(page):
            for j, each_code_m in enumerate(self.encode_check_list):
                try:
                    decode_content = raw_content.decode(each_code_m)
                    if self.page_num is None:
                        self.page_num = len(decode_content)/10000
                        self.page_num = int(self.page_num)+1 if self.page_num > int(self.page_num) else int(self.page_num)
                    book_content = decode_content[(page-1)*10000: page*10000]
                    return book_content
                except:
                    if j==len(self.encode_check_list)-1:
                        return f"文件解码失败"
                    # print(f"{each_code_m}解码失败, 换一种解码方式读取")

# f = Txt("/Users/15400155/Desktop/note/第一次亲密接触.txt")


from PIL import Image
class myImage:
    def __init__(self, data):
        self.content_type = "image/png"
        self.alt_text = ""
        self.data = data

    def open(self):
        return self.data

def convert_image(image):
    with image.open() as image_fileobj:
        # raw_image_data = BytesIO()
        # shutil.copyfileobj(image_fileobj, raw_image_data) Python中的方法用于将file-like对象的内容复制到另一个file-like对象
        raw_image_data = BytesIO(image_fileobj.read()) # 原始图片数据
        raw_image_data.seek(0)
        new_image_data = BytesIO()
        Image.open(raw_image_data).save(new_image_data, format="png")
        new_image_data.seek(0)
    return mammoth.images.data_uri(myImage(new_image_data))


class Docx2Html:
    def __init__(self, file_path):
        '''
        1. 检查是否已经存在html文件，不存在则进行转换
        2. 从html扣出目录
        '''
        self.file_path = file_path
        self.html_path = os.path.join(os.path.dirname(self.file_path),
                                 os.path.splitext(os.path.basename(self.file_path))[0] + ".html")
        self.html_index_path = os.path.join(os.path.dirname(self.file_path),
                                      os.path.splitext(os.path.basename(self.file_path))[0] + "_index.txt")
        self.html_index_path2 = os.path.join(os.path.dirname(self.file_path),
                                      os.path.splitext(os.path.basename(self.file_path))[0] + "_index2.txt")

    @property
    def html_data(self):
        html_data = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"></head>\n\n<body>' # 添加头，告诉浏览器utf8打开
        if not os.path.exists(self.html_path):
            # print("转换doc为html")
            with open(self.file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file, convert_image = convert_image)
                # print(result.value)
                html_data += result.value.replace("<table", "<table border=1 cellspacing=0") # 设置表格边框
                # html_data = html_data.encode("") # The generated HTML
                html_data += result.value
                html_data += "</body></html>"
                with open(self.html_path, "wb") as f:
                    f.write(html_data.encode())
                    # print("转换完成！！")
                    f.close()
        else:
            # print("读取html+++++++++++++++")
            try:
                with open(self.html_path, "rb") as f:
                    html_data = f.read()
                    f.close()
                    for each_code in G_encode_list:
                        try:
                            html_data = html_data.decode(each_code)
                            if each_code!="utf8":
                                # print("重新写入html文件") # 防止获取下面的html_index函数读取此文件又出错
                                with open(self.html_path, "wb") as f:
                                    f.write(html_data.encode())
                                    # print("重写成功！！")
                            break
                        except:
                            continue
            except Exception as e:
                # print("读取html出错", str(e))
                pass
            # print("返回html")
        return html_data

    @property
    def html_index(self):
        result = ""
        if os.path.exists(self.html_index_path):
            # print("目录存在")
            with open(self.html_index_path, "r") as f:
                result = f.read()
                f.close()
        else:
            # print("新建目录")
            with open(self.html_path, "r") as f:
                soup = BeautifulSoup(f, "lxml")
                link = soup.find_all('a')
                for each_tag in link:
                    if "href" in each_tag.attrs:
                        # print(each_tag.string) # 获取值
                        # print(each_tag.get_text()) # 获取值，同上
                        # print(each_tag) # 获取这个标签的所有内容
                        i = 0
                        parent_tag = each_tag
                        retry = 2
                        while i<retry:  # 查找a标签的上面两层标签，看是否含有p标签
                            parent_tag = parent_tag.parent
                            # print(parent_tag.name)
                            if "p" == parent_tag.name: # 使用原来的目录样式
                                if str(parent_tag) not in result:
                                    result += str(parent_tag)
                                break
                            i += 1
                        if i>=retry:
                            if f"<p>{str(each_tag)}</p>" not in result:
                                result += f"<p>{str(each_tag)}</p>"  # 加p换行
                with open(self.html_index_path, "w") as f:
                    f.write(result)
                    f.close()
        # print("获取目录完成！！")
        return result

    @property
    def html_index2(self):
        # 判断self.html_path文件是否存在，不存在先生成
        # print("+++++++++++++++", self.html_path)
        if not os.path.exists(self.html_path):
            data = self.html_data
        result = []
        if os.path.exists(self.html_index_path2):
            with open(self.html_index_path2, "rb") as f:
                result = pickle.load(f)
                # print("目录存在", result)
                f.close()
        else:
            # print("新建目录")
            with open(self.html_path, "r") as f:
                soup = BeautifulSoup(f, "lxml")
                link = soup.find_all('a')
                for each_tag in link:
                    if "href" in each_tag.attrs:
                        # print("string is +++++++++++", str(each_tag.string)) # 获取值
                        # print("href is +++++++++++", each_tag.attrs['href']) 
                        # # print("tag is +++++++++++", each_tag) # 获取这个标签的所有内容
                        # print("text is +++++++++++", each_tag.get_text())
                        if (str(each_tag.attrs['href']), str(each_tag.get_text())) not in result:
                            result.append((str(each_tag.attrs['href']), str(each_tag.get_text())))
                # print("++++", result)
                with open(self.html_index_path2, "wb") as f:
                    pickle.dump(result, f)
                    f.close()
        # print("获取目录完成！！")
        return result


# a_doc = Docx2Html("C:\\Users\\蓝海梦\\Desktop\\django框架.docx")
# a_doc = Docx2Html("/Users/js-15400155/Desktop/linux基础教程.docx")
# a = a_doc.html_index2


def get_html_link(html_path):
    html_index_path = os.path.join(os.path.dirname(html_path),
                                        os.path.splitext(os.path.basename(html_path))[0] + "_index.txt")
    # print("查找目录")
    result = ''
    if os.path.exists(html_index_path):
        # print("目录存在")
        with open(html_index_path, "r") as f:
            result = f.read()
            f.close()
    else:
        with open(html_path, "r") as f:
            soup = BeautifulSoup(f, "lxml")
            link = soup.find_all('a')
            for each_tag in link:
                if "href" in each_tag.attrs:
                    i = 0
                    parent_tag = each_tag
                    retry = 2
                    while i<retry:
                        parent_tag = parent_tag.parent
                        # print(parent_tag.name)
                        if "p" == parent_tag.name or "li" == parent_tag.name: # 使用原来的目录样式
                            if str(parent_tag) not in result:
                                result += str(parent_tag)
                            break
                        i += 1
                    if i>=retry:
                        if f"<p>{str(each_tag)}</p>" not in result:
                            result += f"<p>{str(each_tag)}</p>"  # 加p换行
            result = result.replace('href="./', 'href="')
            with open(html_index_path, "w") as f:
                f.write(result)
                f.close()
        # print("获取目录完成！！")
    return result



# 通过xml获取docx内容
# class xmlWorksHandler(sax.ContentHandler):
    # def __init__(self, docx_obj):
        # '''
        # struct = [{ "Child_Heading1": [],
                    # "Child_Heading2": [],
                    # "Child_heading3": [],
                    # "start": num,
                    # "end":num,
                    # "picture":[num1, num2...],
                    # "table": [num1, num2]}, # 每个字典是一段主标题内容
        # ]
        # '''
        # self.pg_num, self.pic_num, self.tbl_num = 0, 0, 0
        # self.pg_chapter_num = 0
        # self.is_tbl = False
        # self.docx_obj = docx_obj
        # self.total_p = len(self.docx_obj.paragraphs)
        # # print(f"实际有{len(self.docx_obj.paragraphs)}段落")
        # self.current_struct = {"name":"start",
                            #   "Child_Heading1": [], "Child_Heading2": [], "Child_Heading3": [],
                            #   "start": 0, "end": None, "picture": {}, "table": {}
                            #   }
        # self.docx_sturct = []
#
    # # 元素开始事件处理
    # def startElement(self, tag, attributes):
        # self.CurrentData = tag
        # if tag == "w:tbl" and not self.is_tbl:
            # self.is_tbl = True # 表格开始
        # if tag == "w:drawing":
            # if self.pg_num-1 not in self.current_struct["picture"]:
                # self.current_struct["picture"][self.pg_num-1] = []
            # self.current_struct["picture"][self.pg_num-1].append(self.pic_num)
            # self.pic_num += 1
            # # print(f"{self.docx_obj.paragraphs[self.pg_num - 1].text}++++++后面有图片")
#
    # # 元素结束事件处理
    # def endElement(self, tag):
        # '''
        # self.docx_obj.paragraphs[self.pg_num].style.name 属性有：
        # 1. 目录：toc 1, toc 2, toc 3...
        # 2. 常规：Normal
        # 3. 标题：Heading 1,2,3...
        # 4. 链接: HTML Preformatted
        # 5. List Paragraph
        # '''
        # # print(f"结束{tag}")
        # if tag == "w:p" and not self.is_tbl: # 段落结束
            # style_name = self.docx_obj.paragraphs[self.pg_num].style.name
            # re_heading = re.search("Heading (\d)", style_name)
            # if re_heading is not None:
                # heading_level = int(re_heading.group(1))
                # if heading_level==1: # 重新开始
                    # self.current_struct["end"]=self.pg_num - 1
                    # self.pg_chapter_num = 0
                    # self.docx_sturct.append(self.current_struct)
                    # self.current_struct = {"name":self.docx_obj.paragraphs[self.pg_num].text,
                                        #   "Child_Heading1": [], "Child_Heading2": [], "Child_Heading3": [],
                                        #   "start": self.pg_num, "end": None, "picture": {}, "table": {}
                                        #   }
                # elif heading_level==2:
                    # self.current_struct["Child_Heading1"].append(self.pg_num)
                # elif heading_level==3:
                    # self.current_struct["Child_Heading2"].append(self.pg_num)
                # elif heading_level==4:
                    # self.current_struct["Child_Heading3"].append(self.pg_num)
            # re_heading = re.search("标题 ", style_name) # 特殊标题样式，不能区分是第几类标题
            # if re_heading is not None:
                # if self.pg_chapter_num > 10:
                    # self.current_struct["end"] = self.pg_num - 1
                    # self.pg_chapter_num = 0
                    # self.docx_sturct.append(self.current_struct)
                    # self.current_struct = {"name": self.docx_obj.paragraphs[self.pg_num].text,
                                        #   "Child_Heading1": [], "Child_Heading2": [], "Child_Heading3": [],
                                        #   "start": self.pg_num, "end": None, "picture": {}, "table": {}
                                        #   }
            # self.pg_num += 1
            # if self.pg_num == self.total_p:
                # print("结束解析")
                # self.current_struct["end"] = self.pg_num - 1
                # self.docx_sturct.append(self.current_struct)
#
        # if tag == "w:tbl":
            # self.is_tbl = False
            # if self.pg_num - 1 not in self.current_struct["table"]:
                # self.current_struct["table"][self.pg_num - 1] = []
            # self.current_struct["table"][self.pg_num - 1].append(self.pic_num)
            # self.pic_num += 1
#
#
    # # 内容事件处理
    # def characters(self, content):
        # # print("调用内容", content)
        # pass
#
#
# class MyDocx:
    # def __init__(self, file_path):
        # self.file_path = file_path
        # self.xml_path = "word/document.xml"
        # self.docx_obj = docx.Document(self.file_path)
        # print("文件路径", self.file_path)
#
#
    # @property
    # def doc_structure(self):
        # self.zip_doc = zipfile.ZipFile(self.file_path)
        # index_path = os.path.join(os.path.dirname(self.file_path),
                                #  os.path.splitext(os.path.basename(self.file_path))[0]+"_index.txt")
        # if os.path.exists(index_path):
            # print("索引文件存在")
            # with open(index_path, "r") as f:
                # docx_struct = f.read()
                # return eval(docx_struct)
        # else:
            # # 从压缩文件查找xml文档并转存到stringIO对象，以供parser读取
            # self.xml_data = self.zip_doc.read(self.xml_path).decode()
            # f = StringIO()
            # f.write(self.xml_data)
            # f.seek(0)
#
            # # 创建一个XMLReader
            # parser = sax.make_parser()
            # parser.setFeature(sax.handler.feature_namespaces, 0)
            # # 重写ContextHandler
            # Handler = xmlWorksHandler(self.docx_obj)
            # parser.setContentHandler(Handler)
            # parser.parse(f)
            # # print(f"总共有{Handler.pg_num}段落")
            # docx_struct = Handler.docx_sturct
            # # 将文档的结构 字典保存到文档内部，方便下次直接调用
            # self.zip_doc.close()
            # with open(index_path,"w") as f:
                # f.write(str(docx_struct))
            # return docx_struct
#
#
    # def get_content(self, chapter_index):
        # content = ""
        # chapter = self.doc_structure[chapter_index]
        # # print(chapter)
        # name = chapter["name"]
        # for i in range(chapter["start"], chapter["end"]+1):
            # # 转化为html
            # # 添加文字
            # text = self.docx_obj.paragraphs[i].text
            # if i in chapter["Child_Heading1"]:
                # # print("二级标题", text)
                # content += f"<h2>{text}</h2>"
            # elif i in chapter["Child_Heading2"]:
                # # print("三级标题", text)
                # content += f"<h3>{text}</h3>"
            # elif i in chapter["Child_Heading3"]:
                # # print("四级标题", text)
                # content += f"<h4>{text}</h4>"
            # else:
                # content += f"<p>{text}</p>"
#
            # if i in chapter["picture"]:
                # # 添加图片
                # for each_pic in chapter["picture"][i]:
                    # content += "这是一张图片"
            # if i in chapter["table"]:
                # # 添加图片
                # for each_pic in chapter["table"][i]:
                    # content += "这是一个表格"
        # # print(content)
        # return content



# 主函数
# f = MyDocx("/Users/js-15400155/Desktop/HS_server_django/static/HS_server/python_doc/Python基础.docx")
# start_time = time.time()
# print("开始运行")
# f.get_content(0)
# end_time = time.time()
# print(f"运行完成, 耗时{end_time-start_time}s")

# 教程
# XML是指可扩展标记语言，被设计用来传输和存储数据。本章节使用的XML实例文件works.xml内容如下：
# <collection shelf="New Arrivals">
# <works title="电影">
#  <names>敦刻尔克</names>
#  <author>诺兰</author>
# </works>
# <works title="书籍">
#  <names>我的职业是小说家</names>
#  <author>村上春树</author>
# </works>
# </collection>
# Python对XML的解析采用SAX (simple API for XML )模块。

# python 标准库包含SAX解析器，SAX是一种基于事件驱动的API，通过在解析XML的过程中触发一个个的事件并调用用户定义的回调函数来处理XML文件。利用SAX解析XML文档牵涉到两个部分:解析器和事件处理器。解析器负责读取XML文档,并向事件处理器发送事件,如元素开始跟元素结束事件;而事件处理器则负责对事件作出相应,对传递的XML数据进行处理。在python中使用sax方式处理xml要先引入xml.sax.parse()，还有xml.sax.handler.ContentHandler。

# ContentHandler类方法介绍:

# characters(content)方法:

# 调用时机：

# 从行开始，遇到标签之前，存在字符，content的值为这些字符串。

# 从一个标签，遇到下一个标签之前， 存在字符，content的值为这些字符串。

# 从一个标签，遇到行结束符之前，存在字符，content的值为这些字符串。

# 标签可以是开始标签，也可以是结束标签。

# startElement(name, attrs)方法:

# 遇到XML开始标签时调用，name是标签的名字，attrs是标签的属性值字典。

# endElement(name)方法:

# 遇到XML结束标签时调用。

# make_parser方法:

# 以下方法创建一个新的解析器对象并返回。

# xml.sax.make_parser( [parser_list] )

# 参数说明:

# parser_list - 可选参数，解析器列表
# parser方法

# 以下方法创建一个 SAX 解析器并解析xml文档：

# xml.sax.parse( xmlfile, contenthandler[, errorhandler])

# 参数说明:

# xmlfile - xml文件名
# contenthandler - 必须是一个ContentHandler的对象
# errorhandler - 如果指定该参数，errorhandler必须是一个SAX ErrorHandler对象
# Python解析XML实例:

# #!/usr/bin/python3
# #encoding=utf-8

# import xml.sax
# import xml.sax.handler

# class WorksHandler(xml.sax.ContentHandler):
    # def __init__(self):
        # self.CurrentData = ""
        # self.names = ""
        # self.author = ""
    # #元素开始事件处理
    # def startElement(self, tag, attributes):
        # self.CurrentData = tag
        # if tag == "works":
            # print("***内容***")
            # title = attributes["title"]
            # print("类型：",title)
    # #元素结束事件处理
    # def endElement(self, tag):
        # if self.CurrentData == "names":
            # print("名称：",self.names)
        # elif self.CurrentData == "author":
            # print("作者：",self.author)
        # self.CurrentData = ""
    # #内容事件处理
    # def characters(self, content):
        # if self.CurrentData == "names":
            # self.names = content
        # elif self.CurrentData == "author":
            # self.author = content

# if (__name__ == "__main__"):
    # #创建一个XMLReader
    # parser = xml.sax.make_parser()
    # parser.setFeature(xml.sax.handler.feature_namespaces,0)
    # #重写ContextHandler
    # Handler = WorksHandler()
    # parser.setContentHandler(Handler)
    # parser.parse("works.xml")