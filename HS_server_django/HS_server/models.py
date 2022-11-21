from django.db import models
import os

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=50, default="", null=True,  blank=True)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    # url = models.URLField(max_length=100, default="")
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name

class Python_doc(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name
        
class English_doc(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name

class College_doc(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name

class Health_Sensing_doc(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name
        
class HWTE_Station_doc(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name
        
class Python_module(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    format = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name


# # 将图书添加到数据库
# book_dir_all = "/Users/js-15400155/Desktop/note"
# book_dir_all = "/home/haimeng/HS_server_django/static/HS_server/note"
# for current_path, include_dir, include_file in os.walk(book_dir_all):
#     # path = current_path.replace("/Users/js-15400155/Desktop/", "HS_server/")
#     path = current_path.replace("/home/haimeng/HS_server_django/static/HS_server/", "HS_server/")
#     print(path)
#     for i in include_file:
#         book_name = os.path.splitext(i)[0]
#         is_exist_book = Book.objects.filter(name=book_name).exists()
#         print(f"添加{book_name}")
#         # print(f"检查书籍{book_name}是否存在，结果是{is_exist_book}")
#         if is_exist_book:
#             print("此书已存在", book_name)
#         else:
#             if ".DS_Store" not in book_name:
#                 b = Book()
#                 b.name = book_name
#                 b.path = path
#                 b.format = os.path.splitext(i)[1]
#                 b.save()
# print("添加完成++++++++++")



# 将模块添加到数据库
# target_dir = "/Users/js-15400155/Desktop/HS_server_django/static/HS_server/python_doc/HealthSensing"
# target_dir = "/home/haimeng/HS_server_django/static/HS_server/python_doc/pdf"
# for current_path, include_dir, include_file in os.walk(target_dir):
#     path = current_path.replace("/home/haimeng/HS_server_django/static/HS_server/", "HS_server/")
#     print("开始添加目录", path, end=" ")
#     for i in include_file:
#         book_name = os.path.splitext(i)[0]
#         is_exist_book = Python_doc.objects.filter(name=book_name).exists()
#         if is_exist_book:
#             print("失败，目标已存在", book_name)
#         else:
#             if ".DS_Store" not in book_name:
#                 b = Python_doc()
#                 b.name = book_name
#                 b.path = os.path.join(path, i)
#                 b.format = os.path.splitext(i)[1]
#                 b.save()
#                 print(f"添加{book_name}完成")
# print("添加完成++++++++++")

