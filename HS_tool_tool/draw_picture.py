#! /usr/bin/env python3
# ! /usr/bin/env python
import re
import os
import sys
import time
import math
import random
from time import sleep
import threading
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pool
from multiprocessing import Manager

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage


from datetime import datetime
import csv
import xlwt
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.dates as mdate
import matplotlib.mlab as mlab
import numpy as np
from scipy.stats import norm
from io import BytesIO
from PIL import Image, ImageTk
from haimeng_xlwt import Haimeng_xlwt

import platform
if platform.system() == "Windows":
    import ctypes
    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    print("缩放系数是", ScaleFactor)
    # import pathos
    # from pathos.multiprocessing import ProcessingPool

def change_photo(file_path, width, is_zoomout=False, is_square=False, height=None):
    try:
        image = Image.open(file_path)
        image_size = image.size  # (宽，高)
        if width < image_size[0] or is_zoomout:  # 小的图片不放大，除非指定is_zoomout为True
            if height is not None:
                image_size = (width, height)
            else:
                image_size = (width, int(image_size[1] / image_size[0] * width))
        if is_square:
            image_size = (image_size[0], image_size[0])
        image = image.resize(image_size)
        photo = ImageTk.PhotoImage(image)
        # image.save("/Users/15400155/Desktop/haimeng.png")
        return photo, image_size
    except Exception as e:
        print("change picture failed",str(e), file_path)
        return None, None


class Insight_csv_data:
    def __init__(self, csv_file_path):
        """
        1. 读取csv， 生成：
            1）由多个csv合并的 csv列表self.csv_list
            2）self.unit_test_record = [{"Site": "ITJS","SerialNumber": "SN1"...},
                                        {"Site": "ITJS2","SerialNumber": "SN2"...}...]
            3）self.item_name_list = ["AC_CP", "xxx"...]
            4) self.test_item_limit = {
                                        each_item:{
                                            "Upper Limit":read_all_csv_list[4][item_name_list.index(each_item)],
                                            "Lower Limit":read_all_csv_list[5][item_name_list.index(each_item)],
                                            "Measurement Unit":read_all_csv_list[6][item_name_list.index(each_item)]
                                        }...}
        2. 获取self.input_detail_data= {
                                            "total_input": input num,
                                            "total_fail": fail num,
                                            station + "_sum" : station sum,
                                            station + "_fail_sum": station_fail_sum
                                            station: {
                                                sn: station_sn_num
                                                sn+"_fail" : station_sn_fail_num
                                            }
                                        }
        """
        self.progress_label,self.progress_bar = None,None
        self.color_by_list = ["all_data", "SerialNumber", "Special Build Description", "Station ID"]
        self.current_finish_search_item = []
        self.load_data_process_list = []
        self.is_finish_load_data = False
        self.load_data_quene = None
        self.station_id_list, self.sn_list = [], []
        self.current_progress, self.total_progress = 0, 0
        self.distinguish_data, self.xx_list_dict, self.station_sn_data = {}, {}, {}

        self.csv_list, self.unit_test_record, self.item_name_list, self.test_item_limit = self.read_csv(csv_file_path)
        print(self.item_name_list)
        self.input_detail_data = self.search_input_detail_data(self.unit_test_record)

    def write_csv(self, file_path, value_list):
        f = open(file_path, 'w', encoding='utf-8')
        csv_writer = csv.writer(f)
        for each_line in value_list:
            csv_writer.writerow(each_line)
        f.close()

    def merge_csv(self, read_all_csv_list, read_csv, measurement_start):
        current_title = read_csv[1][:]
        exist_title = read_all_csv_list[1][:]
        # 更新标题
        for each_name in current_title:
            if each_name not in exist_title:
                exist_title.append(each_name)  # 添加新增测试项
                row = 0
                for each_line in read_csv[:measurement_start]:  # 添加新测试项的limit、unit等
                    read_all_csv_list[row].append(each_line[current_title.index(each_name)])
                    row += 1
        # 添加测试值
        for each_line in read_csv[measurement_start:]:
            add_line = [""] * len(exist_title)
            for each_name in current_title:
                add_line[exist_title.index(each_name)] = each_line[current_title.index(each_name)]
            read_all_csv_list.append(add_line)
        return read_all_csv_list

    def get_unit_test_records(self, read_all_csv_list):
        '''
            return:
            1. unit_test_record = [{"Site": "ITJS","SerialNumber": "SN1"...},
                                    {"Site": "ITJS2","SerialNumber": "SN2"...}...]
            2. item_name_list = ["AC_CP", "xxx"...]
            3. test_item_limit = {
                                    each_item:{
                                        "Upper Limit":read_all_csv_list[4][item_name_list.index(each_item)],
                                        "Lower Limit":read_all_csv_list[5][item_name_list.index(each_item)],
                                        "Measurement Unit":read_all_csv_list[6][item_name_list.index(each_item)]
                                    }...}
        '''
        unit_test_record = []
        test_item_limit = {}
        if read_all_csv_list[1][0] == "Site":
            measurement_start = 7
            # 获取测试项开始的列数
            try:
                test_item_start = read_all_csv_list[0].index("Parametric")
            except:
                for each_column in range(len(read_all_csv_list[3])):
                    if read_all_csv_list[3][each_column] != "" and each_column != 0 and self.is_float(
                            read_all_csv_list[8][each_column]):
                        test_item_start = each_column
                        break
            # 获取测试项列表
            item_name_list = read_all_csv_list[1][test_item_start:]
            title_line = read_all_csv_list[1]
            # 获取limit
            for each_item in item_name_list:
                if each_item not in test_item_limit:
                    test_item_limit[each_item] = {}
                test_item_limit[each_item] = {
                    "Upper Limit": read_all_csv_list[4][test_item_start + item_name_list.index(each_item)],
                    "Lower Limit": read_all_csv_list[5][test_item_start + item_name_list.index(each_item)],
                    "Measurement Unit": read_all_csv_list[6][test_item_start + item_name_list.index(each_item)]
                }
        else:
            measurement_start = 1
            test_item_start = 0
            item_name_list = read_all_csv_list[0]
            title_line = read_all_csv_list[0]
            for each_item in item_name_list:
                if each_item not in test_item_limit:
                    test_item_limit[each_item] = {}
                test_item_limit[each_item] = {
                    "Upper Limit": "NA",
                    "Lower Limit": "NA",
                    "Measurement Unit": "NA"
                }
        # 获取每一行每一列的值，我也不知道最初为什么要用这种方法。。。
        for each_line in range(len(read_all_csv_list[measurement_start:])):
            if read_all_csv_list[each_line + measurement_start] != []:
                unit_test_record.append({})
                for each_column in range(len(title_line)):
                    key = title_line[each_column]
                    try:
                        value = read_all_csv_list[each_line + measurement_start][each_column]
                    except:
                        value = ''
                    unit_test_record[each_line][key] = value
        return unit_test_record, item_name_list, test_item_limit

    def read_csv(self, file_path_list):
        """
        读取csv并生成画图数据
        """
        unit_test_record = []
        read_all_csv_list = []
        test_item_limit = {}
        file_num = 0
        for each_file in file_path_list:
            file_num += 1
            # 合并文件为一个list
            with open(each_file, encoding='utf-8') as csvf:
                read_csv = list(csv.reader(csvf))
                if read_csv[1][0] == "Site":
                    measurement_start = 7
                else:
                    measurement_start = 1
                if file_num == 1:
                    read_all_csv_list = [each_line[:] for each_line in read_csv]
                else:
                    # 合并不同的csv 文件
                    read_all_csv_list = self.merge_csv(read_all_csv_list, read_csv, measurement_start)
        unit_test_record, item_name_list, test_item_limit = self.get_unit_test_records(read_all_csv_list)
        # self.write_csv(os.path.join(os.path.dirname(file_path_list[0]),"merge.csv"),read_all_csv_list)
        # print(unit_test_record)
        return read_all_csv_list, unit_test_record, item_name_list, test_item_limit

    def search_input_detail_data(self, unit_test_record):
        '''
            input_detail_data = {
                                    "total_input": input num,
                                    "total_fail": fail num,
                                    station + "_sum" : station sum,
                                    station + "_fail_sum": station_fail_sum
                                    station: {
                                        sn: station_sn_num
                                        sn+"_fail" : station_sn_fail_num
                                    }
                                }
        '''
        input_detail_data = {}
        input_detail_data["total_input"] = 0
        input_detail_data["total_fail"] = 0
        for each_line in unit_test_record:
            station = each_line["Station ID"]
            sn = each_line["SerialNumber"]
            if station not in self.station_id_list:
                self.station_id_list.append(station)
            if sn not in self.sn_list:
                self.sn_list.append(sn)

            fail_pass = each_line["Test Pass/Fail Status"]

            input_detail_data["total_input"] += 1
            if fail_pass == "FAIL":
                input_detail_data["total_fail"] += 1
            if station not in input_detail_data.keys():
                input_detail_data[station] = {}  # input_detail_data["TEST5"] = {}

            if station + "_sum" not in input_detail_data.keys():
                input_detail_data[station + "_sum"] = 1  # input_detail_data["TEST5"] = {}
            else:
                input_detail_data[station + "_sum"] += 1

            if station + "_fail_sum" not in input_detail_data.keys():
                input_detail_data[station + "_fail_sum"] = 0  # input_detail_data["TEST5"] = {}
                if fail_pass == "FAIL":
                    input_detail_data[station + "_fail_sum"] = 1
            else:
                if fail_pass == "FAIL":
                    input_detail_data[station + "_fail_sum"] += 1

            if sn not in input_detail_data[station].keys():
                input_detail_data[station][sn] = 1
                if sn + "_fail" not in input_detail_data[station].keys():
                    input_detail_data[station][sn + "_fail"] = 0
                    if fail_pass == "FAIL":
                        input_detail_data[station][sn + "_fail"] = 1
            else:
                input_detail_data[station][sn] += 1
                if fail_pass == "FAIL":
                    input_detail_data[station][sn + "_fail"] += 1
        return input_detail_data



    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                           以下函数由其他类调用
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def search_xx_list(self, xx_list_dict, item_name_list, unit_test_record, color_by_list):
        '''
        xx_list_dict = {"AC_CP":{
            "all":[all]
            "SN":[SN1,SN2,...]
            "station":[station1,station2,...]
            "config": [...]
            }
        }
        '''
        # xx_list_dict = {}
        for each_item in item_name_list:
            if each_item not in xx_list_dict:
                xx_list_dict[each_item] = {}
            for each_color_by in color_by_list:
                if each_color_by not in xx_list_dict[each_item]:
                    xx_list_dict[each_item][each_color_by] = []
                if each_color_by == "all_data":
                    xx_list_dict[each_item][each_color_by].append("all_data")
                    continue
                else:
                    for each_line in unit_test_record:
                        if each_line[each_color_by] not in xx_list_dict[each_item][each_color_by]:
                            xx_list_dict[each_item][each_color_by].append(each_line[each_color_by])
                self.current_progress += 1
        return xx_list_dict

    def search_station_sn_data(self, station_sn_data,unit_test_record, item_name_list):
        '''
            station_sn_data["AC_CP"]["station"]["sn"] = [value_list]
        '''
        for each_item in item_name_list:
            if each_item not in station_sn_data:
                station_sn_data[each_item] = {}
            for each_line in unit_test_record:
                station = each_line["Station ID"]
                sn = each_line["SerialNumber"]
                if station not in station_sn_data[each_item]:
                    station_sn_data[each_item][station] = {}
                if sn not in station_sn_data[each_item][station]:
                    station_sn_data[each_item][station][sn] = []
                measurement_value = self.get_measurement(each_line, each_item)
                if measurement_value != None:
                    station_sn_data[each_item][station][sn].append(measurement_value)
                # Todo else?
                self.current_progress += 1
        return station_sn_data

    def is_time(self, string):
        # 目前只识别：2021-10-01 10:08:09, 2021-10-01 10:08, 2021/10/01 10:08:09, 2021/10/01 10:08 四种类型
        time_re = re.search(r'^(\d{4}).(\d+).(\d+).(\d+):(\d+):*(\d*)', string)
        if time_re != None:
            return True
        else:
            return False

    def get_time(self, each_line):
        time = None
        try:
            if each_line["StartTime"] != "":
                time = each_line["StartTime"]
                if not self.is_time(each_line["StartTime"]):
                    print("Error", "获取%s的测试时间出错啦,%s可能不是有效时间" % (
                        each_line["SerialNumber"], each_line["StartTime"]))
            else:  # 没测试时间
                time = ''
                print("Error", "获取%s的测试时间出错啦,时间为空值" % (each_line["SerialNumber"]))
        except:
            time = ''
            print("获取时间出错", each_line)
        return time

    def is_float(self, string):
        i = 0
        for each_s in string:
            i += 1
            if not each_s.isdigit() and each_s != ".":
                if i == 1:
                    if each_s == "-":
                        continue
                else:
                    return False
            else:
                return True

    def get_measurement(self, each_line, item):
        measurement_value = None
        if each_line[item] != "":
            measurement_value = float(each_line[item])
            if not self.is_float(each_line[item]):
                print("Error", "获取%s的%s测试值出错啦,测试值为%s该值可能不是数字" % (
                    each_line["SerialNumber"], item, each_line[item]))
        else:
            measurement_value = 0.000141747
        return measurement_value

    def compare_test_time(self, new_csv_time, old_csv_time):
        new_max = old_csv_time
        if '-' in new_csv_time:

            if not self.is_time(new_csv_time) or not self.is_time(old_csv_time):
                print("Hi", "compare test time error,cause time format error")
                return None
            else:
                time_new = self.change_time_tuple(new_csv_time)
                time_max_old = self.change_time_tuple(old_csv_time)
                for each_new in range(len(time_new)):
                    if time_new[each_new] > time_max_old[each_new]:
                        return True
                    elif time_new[each_new] < time_max_old[each_new]:
                        return False
                    else:
                        continue
                return True  # 两个值相等

    def change_time_tuple(self, time):
        time_re = re.search(r'^(\d{4}).(\d+).(\d+).(\d+):(\d+):*(\d*)', time)
        return (
            time_re.group(1), time_re.group(2), time_re.group(3), time_re.group(4), time_re.group(5), time_re.group(6))

    def is_fail_value(self, measurement_value, upper_limit, lower_limit):
        if measurement_value != "" and measurement_value != 0.000141747:
            if upper_limit != "NA" and upper_limit != "":
                if float(measurement_value) > float(upper_limit):
                    return True
            if lower_limit != "NA" and lower_limit != "":
                if float(measurement_value) < float(lower_limit):
                    return True
            return False
        else:
            return False

    def search_distinguish_data(self, distinguish_data, unit_test_record, item_name_list, color_by_list, test_item_limit):
        '''
            查找区分 all/SN/station/config 数据
            包含信息： 测试项，x轴， y轴， 按什么来区分
            distinguish_data = {
                "AC_CP":{
                    "all_data":{
                        "all_data":{
                            "time_value" = [],
                            "y_value" = [],
                            "total test",
                            "fail num"
                        }}
                    "SN":{
                        "SN1":{
                            "time_value" = [],
                            "y_value" = [],
                            "total test",
                            "fail num"
                        }
                        "SN2":{
                            "time_value" = [],
                            "y_value" = [],
                            "total test",
                            "fail num"
                        }
                    }
                    "station":{}
                    "config":{}
                }
                "Crown_force":{
                    "all_data":{}
                    "SN":{}
                    "station":{}
                    "config":{}
                }
            }
        '''
        #distinguish_data = {}
        if "Site" not in unit_test_record[0]:
            is_insight_csv = False
            new_color_by_list = [color_by_list[0]]
        else:
            new_color_by_list = color_by_list
            is_insight_csv = True

        for each_item in item_name_list:
            if each_item not in distinguish_data:
                distinguish_data[each_item] = {}
            print(new_color_by_list)
            for each_color_by in new_color_by_list:
                if each_color_by not in distinguish_data[each_item]:
                    # distinguish_data["AC_CP"]["all_data/SN/station/config"] = {}
                    distinguish_data[each_item][each_color_by] = {}
                for each_line in unit_test_record:
                    # 判断该使用什么键名
                    # print(each_line)
                    if is_insight_csv:
                        if each_color_by != "all_data":
                            current_xx = each_line[each_color_by]  # 具体的哪个SN/station ID
                        else:
                            current_xx = "all_data"
                    else:
                        current_xx = "all_data"
                    # 添加键名
                    if current_xx not in distinguish_data[each_item][each_color_by]:
                        distinguish_data[each_item][each_color_by][current_xx] = {}

                    # 开始添加数据
                    if is_insight_csv:
                        # 添加时间
                        if "time_value" not in distinguish_data[each_item][each_color_by][current_xx]:
                            distinguish_data[each_item][each_color_by][current_xx]["time_value"] = []
                        time = self.get_time(each_line)
                        if time != None:
                            distinguish_data[each_item][each_color_by][current_xx]["time_value"].append(
                                each_line["StartTime"])
                        # Todo else?
                    # 添加测试值
                    if "y_value" not in distinguish_data[each_item][each_color_by][current_xx]:
                        distinguish_data[each_item][each_color_by][current_xx]["y_value"] = []
                    measurement_value = self.get_measurement(each_line, each_item)
                    if measurement_value != None:
                        distinguish_data[each_item][each_color_by][current_xx]["y_value"].append(measurement_value)
                    # Todo else?
                    if "total test" not in distinguish_data[each_item][each_color_by][current_xx]:
                        distinguish_data[each_item][each_color_by][current_xx]["total test"] = 0
                    distinguish_data[each_item][each_color_by][current_xx]["total test"] += 1
                    if "fail num" not in distinguish_data[each_item][each_color_by][current_xx]:
                        distinguish_data[each_item][each_color_by][current_xx]["fail num"] = 0
                    if self.is_fail_value(measurement_value, test_item_limit[each_item]["Upper Limit"],
                                          test_item_limit[each_item]["Lower Limit"]):
                        distinguish_data[each_item][each_color_by][current_xx]["fail num"] += 1
                    self.current_progress+=1
        return distinguish_data

    def search_item_data(self,item_name_list):
        """
        1. 获取各个测试项的数据
            distinguish_data ={"AC_CP":{"all_data":{ "all_data":{"time_value" = [],"y_value" = [],"total test","fail num"}},
                                        "SN":{"SN1":{"time_value" = [],"y_value" = [],"total test","fail num"}, "SN2"...}
                                        "station":{...}...}
        2. 获取每个测试项对应的不同SN/station/config类型
            xx_list_dict = {"AC_CP":{"all":[all]
                                    "SN":[SN1,SN2,...]
                                    "station":[station1,station2,...]
                                    "config": [...]
                                    }
                            }
        3. 获取不同Station不同SN对应的测试值
            station_sn_data["AC_CP"]["station"]["sn"] = [value_list]
        """
        distinguish_data = {}
        xx_list_dict = {}
        station_sn_data = {}
        for item_name in item_name_list:
            if item_name not in self.current_finish_search_item or item_name=='':

                distinguish_data = self.search_distinguish_data({},self.unit_test_record,
                                                        [item_name],self.color_by_list,self.test_item_limit)
                # 获取SN/Station/config列表
                xx_list_dict = self.search_xx_list({}, [item_name], self.unit_test_record, self.color_by_list)
                station_sn_data = self.search_station_sn_data({},self.unit_test_record, [item_name])
                self.current_finish_search_item.append(item_name)
            # 返回值用于多进程
        return [distinguish_data,xx_list_dict,station_sn_data]

    def load_data_process_fun(self,q,item_name_list):
        """
        多进程获取数据函数
        """
        for each_item in item_name_list:
            result = self.search_item_data([each_item])
            q.put(result)
            sleep(0.1)

    def load_data_process(self):
        """
        将测试项平均分给多个进程来获取数据： self.load_data_process_fun 为获取数据函数
        如果还有剩余测项没被获取，继续获取数据
        self.load_data_process_list 保存每个进程
        """
        self.real_run_process_num = 0  # 开启的进程数量
        current_item_num = 0  # 当前已经放进进程的测试项数量
        end_num = 0  # while调用完成后，已放进进程的总测项
        while current_item_num < len(self.item_name_list[:]):
            end_num += int(len(self.item_name_list[:])/self.set_process_num)

            load_data_process = Process(target=self.load_data_process_fun,
                        args=(self.load_data_quene,self.item_name_list[current_item_num:end_num]))
            load_data_process.start()
            self.load_data_process_list.append(load_data_process)
            self.real_run_process_num += 1
            #print(f"正在执行item list{current_item_num, end_num},进程{self.real_run_process_num}")
            current_item_num += int(len(self.item_name_list[:]) / self.set_process_num)
            sleep(0.01)
        # 剩余测项继续调用加载数据
        if end_num <= len(self.item_name_list[:]):
            load_data_process = Process(target=self.load_data_process_fun,
                            args=(self.load_data_quene, self.item_name_list[end_num:len(self.item_name_list[:])]))
            load_data_process.start()
            self.load_data_process_list.append(load_data_process)
            self.real_run_process_num += 1

    def start_load_picture_data(self):
        """
        多进程加载全部数据: 进程数最大为15个
        """
        self.set_process_num = len(self.item_name_list) / 15
        if self.set_process_num > 15:
            self.set_process_num = 15
        elif self.set_process_num == 0:
            self.set_process_num = 1

        print("开启多进程获取数据+++++++++++++++++++++")
        self.load_data_quene = Queue(int(self.set_process_num))
        self.load_data_process()
        # self.load_data_process_threading = threading.Thread(target=self.load_data_process)
        # self.load_data_process_threading.setDaemon(True)
        # self.load_data_process_threading.start()

    def show_progress(self,item_name):
        while True:
            try:
                self.progress_label["text"] = f"Loading current item:"
                self.progress_bar["value"] = self.current_progress/self.total_progress*100
                if self.is_finish_load_data:
                    self.progress_bar["value"] = 100
                    break
            except Exception as e:
                print(e)
            sleep(0.01)

    def search_item_data_with_progress(self,item_name_list,label,progress_bar):
        """
        获取指定测项的数据，并且显示获取进度条
        """
        self.progress_label, self.progress_bar = label,progress_bar
        self.is_finish_load_data = False
        self.total_progress = len(self.color_by_list) * len(self.unit_test_record) + \
                              len(self.color_by_list) + len(self.unit_test_record)
        self.current_progress = 0  # 当前加载数据进度
        self.show_progress_threading = threading.Thread(target=self.show_progress,args=(str(item_name_list[0]),))
        self.show_progress_threading.setDaemon(True)
        self.show_progress_threading.start()

        [distinguish_data,xx_list_dict,station_sn_data] = self.search_item_data(item_name_list)
        self.is_finish_load_data = True
        return [distinguish_data,xx_list_dict,station_sn_data]


class Calculate_GRR(Insight_csv_data):
    def __init__(self):
        self.current_progress, self.total_progress = 0, 0

    def generate_GRR_data(self, csv_list, times,slot, is_save_csv=True):
        self.generate_GRR_times = times
        self.generate_GRR_data_slot = slot

        data_startline_index = 7
        try:
            station_index = csv_list[1].index("Station ID")
        except:
            station_index = csv_list[1].index("TesterID")
        sn_index = csv_list[1].index("SerialNumber")
        fail_pass_index = csv_list[1].index("Test Pass/Fail Status")
        test_time_index = csv_list[1].index("StartTime")

        if self.generate_GRR_times == "" or not self.generate_GRR_times.isdigit():
            # tk.messagebox.showinfo(title="Hi", message="input a number to times entry first!")
            #self.generate_GRR_times.set(5)  # 如果没指定数量，设置为5
            self.generate_GRR_times = 5

        if self.generate_GRR_data_slot != "":  # "slot_ID"
            if self.generate_GRR_data_slot.isdigit():
                slot_index = csv_list[0].index("Parametric") + int(self.generate_GRR_data_slot)
            else:
                slot_name = self.generate_GRR_data_slot
                slot_index = csv_list[1].index(slot_name)
            # ----- 合并slot ---------
            new_csv_list = []
            row = 0
            # 修改station名字 为加 slot
            for each_line in csv_list:
                if row >= data_startline_index:
                    each_line[station_index] = each_line[station_index] + "_slot" + each_line[slot_index]
                new_csv_list.append(each_line)
                row += 1
            self.export_csv_list = new_csv_list

        # --------- 生成GRR csv ------------
        new_csv_list = []
        self.generate_GRR_data_dict = {}  # 测试次数统计
        row = 0
        for each_line in csv_list:
            if row < data_startline_index:  # 数据行之前的行保留
                new_line = []
                new_csv_list.append(each_line)
                row += 1
            else:
                new_line = []
                SN = each_line[sn_index]
                Station = each_line[station_index]
                fail_pass = each_line[fail_pass_index]

                if fail_pass == "PASS" or fail_pass == "FAIL":  # 只要PASS 的数据
                    if SN not in self.generate_GRR_data_dict.keys():
                        self.generate_GRR_data_dict[SN] = {}
                    if Station not in self.generate_GRR_data_dict[SN].keys():
                        self.generate_GRR_data_dict[SN][Station] = 1
                    else:
                        self.generate_GRR_data_dict[SN][Station] += 1
                    # 如果当前Station 的 当前SN 测试次数小于 需要截取的测试次数，直接添加数据
                    if int(self.generate_GRR_data_dict[SN][Station]) <= int(self.generate_GRR_times):
                        new_csv_list.append(each_line)
                    # 如果当前Station 的 当前SN 测试次数大于 需要截取的测试次数，则挑选出测试时间靠后的数据
                    elif int(self.generate_GRR_data_dict[SN][Station]) > int(self.generate_GRR_times):
                        min_time = []
                        for new_each_line in new_csv_list:
                            if new_each_line[sn_index] == SN and new_each_line[station_index] == Station:
                                if min_time == []:
                                    min_time = new_each_line
                                else:
                                    if self.compare_test_time(min_time[test_time_index],
                                                              new_each_line[test_time_index]):
                                        min_time = new_each_line
                        if self.compare_test_time(each_line[test_time_index], min_time[test_time_index]):
                            # 将该行数据与列表中的比较,如果时间比其中最小的一个晚，就替换掉
                            new_csv_list[new_csv_list.index(min_time)] = each_line
        # 校验测试次数
        is_test_times_ok = False
        for each_sn in self.generate_GRR_data_dict:
            for each_station in self.generate_GRR_data_dict[each_sn]:
                if int(self.generate_GRR_data_dict[each_sn][each_station]) < int(self.generate_GRR_times):
                    tk.messagebox.showerror("Error", "%s 机台 在%s 站位的测试次数只有%d, 小于%d" % (each_sn, each_station,
                                                                                      int(self.generate_GRR_data_dict[
                                                                                              each_sn][each_station]),
                                                                                      int(
                                                                                          self.generate_GRR_times)))
                    is_test_times_ok = True
                    break
            if is_test_times_ok:
                break

        if is_save_csv:
            # ---------  开始写入csv ---------------------
            save_path = tkfile.asksaveasfilename(title="choose save path", defaultextension=".csv")
            if save_path != "":
                f = open(save_path, 'w', encoding='utf-8')
                csv_writer = csv.writer(f)
                for each_line in new_csv_list:
                    csv_writer.writerow(each_line)
        return new_csv_list

    def get_GRR_data(self,csv_list,times,slot):
        read_all_csv_list = self.generate_GRR_data(csv_list,times,slot,False)
        unit_test_record, item_name_list, test_item_limit = self.get_unit_test_records(read_all_csv_list)
        color_by_list = ["all_data", "SerialNumber", "Special Build Description", "Station ID"]
        # xx_list_dict = self.search_xx_list(item_name_list,unit_test_record, color_by_list)
        xx_list_dict = self.search_xx_list({}, item_name_list[:1], unit_test_record, color_by_list)
        station_sn_data = self.search_station_sn_data({},unit_test_record, item_name_list)

        return station_sn_data,xx_list_dict,item_name_list,test_item_limit

    def read_grr_sheet(self, grr_sheet_path):
        with open(grr_sheet_path, "r") as grr_sheet_file:
            FOMs_str = ""
            start_record_fom = False
            for each_line in grr_sheet_file:
                if "FOMS" in each_line:
                    start_record_fom = True
                    continue
                if start_record_fom:
                    FOMs_str += each_line
                if "signatures" in each_line:
                    break

        FOMs_dict = {}
        item_name_list = []
        item_name_re = re.search(r'KEY.*:.*"(.+)"\n', FOMs_str)
        while item_name_re != None:
            item_name = item_name_re.group(1)
            FOMs_dict[item_name] = {}
            item_name_list.append(item_name)
            upper_limit_re = re.search(r'UPPER_LIMIT.*?:.*?(.+)\n', FOMs_str)
            lower_limit_re = re.search(r'LOWER_LIMIT.*?:.*?(.+)\n', FOMs_str)
            ptr_threshold_re = re.search(r'PTR_THRESHOLD.*?:.*?(.+)\n', FOMs_str)
            if upper_limit_re != None:
                FOMs_dict[item_name]["Upper Limit"] = upper_limit_re.group(1)
            if lower_limit_re != None:
                FOMs_dict[item_name]["Lower Limit"] = lower_limit_re.group(1)
            if ptr_threshold_re != None:
                FOMs_dict[item_name]["PTR_THRESHOLD"] = ptr_threshold_re.group(1)
            search_end_location = ptr_threshold_re.end()
            FOMs_str = FOMs_str[search_end_location:]
            item_name_re = re.search(r'KEY.*?:.*?"(.+)"\n', FOMs_str)
        if FOMs_dict != {}:
            return FOMs_dict
        else:
            tk.messagebox.showinfo("Hi", "GRR sheet invalid")
            return {}

    def get_GRR_result(self, item_name, station_num, sn_num, lower_limit, upper_limit, station_sn_data):
        test_times = 0
        group_inside_mean = []
        op_mean = []

        SSerror = 0
        for each_station in station_sn_data[item_name]:
            current_group_inside_mean = []
            for each_sn in station_sn_data[item_name][each_station]:
                if test_times < len(station_sn_data[item_name][each_station][each_sn]):
                    test_times = len(station_sn_data[item_name][each_station][each_sn])
                current_sn_array = np.array(station_sn_data[item_name][each_station][each_sn])
                current_sn_data_mean = np.mean(current_sn_array)

                # 计算重复性 error变差
                for each_test_value in station_sn_data[item_name][each_station][each_sn]:
                    SSerror += (each_test_value - current_sn_data_mean) ** 2

                current_group_inside_mean.append(current_sn_data_mean)
            group_inside_mean.append(np.array(current_group_inside_mean))  # 组内平均值
            op_mean.append(np.mean(np.array(current_group_inside_mean)))  # 测试员平均值


        # 自由度计算
        Derror = station_num * sn_num * (test_times - 1)
        Dop = station_num - 1
        Dpart = sn_num - 1
        Dop_part = (station_num - 1) * (sn_num - 1)

        # 计算重复性 变差
        MSSerror = SSerror / (Derror)
        # 计算OP 变差
        total_mean = np.mean(np.array(op_mean))  # 总平均值：
        SSop = 0

        # print("item_name", item_name)
        for each_value in op_mean:
            SSj = (each_value - total_mean) ** 2 * sn_num * test_times
            # print("ssj",SSj)
            SSop += SSj
        MSSop = SSop / (Dop)
        # print("ssop",SSop)
        # print("Msop",MSSop)
        # 计算零件 变差
        sn_mean = np.mean(np.array(group_inside_mean), axis=0)
        SSpart = 0

        for each_sn_value in sn_mean:
            # print("sn_mean",each_sn_value)
            # SSpart += (each_sn_value-total_mean)**2*(station_num*sn_num)
            SSpart += (each_sn_value - total_mean) ** 2 * (station_num * test_times)
        MSSpart = SSpart / (Dpart)
        # print("total", total_mean)
        # print("station_num",station_num)
        # print("sn_num",sn_num)
        # print("sspart",SSpart)
        # print("msprt",MSSpart)
        # print("SSerror",SSerror)
        # print("Mserror",MSSerror)
        # 计算总 变差
        SSt = 0
        for each_station in station_sn_data[item_name]:
            for each_sn in station_sn_data[item_name][each_station]:
                for each_sn_value in station_sn_data[item_name][each_station][each_sn]:
                    SSt += (each_sn_value - total_mean) ** 2
        # 计算交互变差
        SSop_part = SSt - SSpart - SSop - SSerror
        MSSop_part = SSop_part / (Dop_part)
        # print("SSop*part",SSop_part)
        # print("MSSop*part",MSSop_part)
        # print("MSSop:",MSSop,"MSSerror:",MSSerror,"MSSpart:",MSSpart,"MSSop*part:",MSSop_part)

        # sigma_part
        sigma_part_square = (MSSpart - MSSop_part) / (station_num * test_times)
        if sigma_part_square < 0:
            sigma_part_square = 0
        sigma_part = math.sqrt(sigma_part_square)

        # sigma_error
        repeatability_sigma_square = MSSerror
        sigma_error = math.sqrt(repeatability_sigma_square)

        # sigma_op
        sigma_op_square = (MSSop - MSSop_part) / (sn_num * test_times)
        if sigma_op_square < 0:
            sigma_op_square = 0
        sigma_op = math.sqrt(sigma_op_square)

        # sigma_op_part
        sigma_op_part_square = (MSSop_part - MSSerror) / (test_times)
        if sigma_op_part_square < 0:
            sigma_op_part_square = 0
        sigma_op_part = math.sqrt(sigma_op_part_square)

        # 开始计算 GRR
        reproducibility_sigma_square = sigma_op_square + sigma_op_part_square
        GRR_sigma_square = repeatability_sigma_square + reproducibility_sigma_square

        spec = float(upper_limit) - float(lower_limit)
        # print(upper_limit,lower_limit)
        repeatability = math.sqrt(repeatability_sigma_square) * 3 / spec
        reproducibility = math.sqrt(reproducibility_sigma_square) * 3 / spec
        tolerance = math.sqrt(GRR_sigma_square) * 3 / spec
        # Todo 如果数值为空怎么弄？
        return repeatability, reproducibility, tolerance, sigma_part, sigma_op, sigma_op_part, sigma_error


    def write_GRR_excel(self, GRR_excel, FOMs_dict):
        save_path = tkfile.asksaveasfilename(title="choose save path", defaultextension=".xls")
        haimeng_xlwt = Haimeng_xlwt(save_path)
        sheet = haimeng_xlwt.xls_book.add_sheet("GRR report")
        for each_line in range(len(GRR_excel)):
            for each_column in range(len(GRR_excel[each_line])):
                if each_line==0:
                    sheet.write(each_line + 1, each_column, GRR_excel[each_line][each_column], haimeng_xlwt.gray_title_style)
                else:
                    if (each_column==1 or each_column==2):
                        sheet.write(each_line + 1, each_column, GRR_excel[each_line][each_column], haimeng_xlwt.blue_style)
                    elif each_column>=3 and each_column <= 5:
                        if float(GRR_excel[each_line][each_column])<0.1:
                            sheet.write(each_line+1, each_column, "%.3f" % (100 *GRR_excel[each_line][each_column])+"%", haimeng_xlwt.green_style)
                        elif float(GRR_excel[each_line][each_column])>0.3:
                            sheet.write(each_line+1, each_column, "%.3f" % (100 *GRR_excel[each_line][each_column])+"%", haimeng_xlwt.red_style)
                        else:
                            sheet.write(each_line + 1, each_column,"%.3f" % (100 * GRR_excel[each_line][each_column]) + "%", haimeng_xlwt.yellow_style)
                    elif each_column == 6:
                        if GRR_excel[each_line][each_column]=="pass":
                            sheet.write(each_line + 1, each_column, GRR_excel[each_line][each_column], haimeng_xlwt.green_style)
                        elif GRR_excel[each_line][each_column]=="Unacceptable":
                            sheet.write(each_line + 1, each_column, GRR_excel[each_line][each_column], haimeng_xlwt.red_style)
                    else:
                        sheet.write(each_line+1, each_column, GRR_excel[each_line][each_column], haimeng_xlwt.normal_style)
        sheet.col(0).width = 10000
        for each_column in range(len(GRR_excel[1:])):
            sheet.col(each_column+1).width = 3200
        if save_path!="":
            haimeng_xlwt.xls_book.save(save_path)


    def run_GRR_report(self, csv_list,times,slot):
        station_sn_data, xx_list_dict, item_name_list, test_item_limit = self.get_GRR_data(csv_list,times,slot)

        grr_sheet_path = tk.filedialog.askopenfilename(title="choose the GRR SHEET file")
        if grr_sheet_path != "":
            FOMs_dict = self.read_grr_sheet(grr_sheet_path)
        else:
            FOMs_dict = {}

        sn_list = xx_list_dict[item_name_list[0]]["SerialNumber"]
        station_list = xx_list_dict[item_name_list[0]]["Station ID"]
        GRR_excel = []
        GRR_excel.append(["Item_name", "Lowe_limit", "Upper_limit", "Repeatability", "Reproducibility", "Tolerance",
                          "Result", "Sigma_part", "Sigma_factor", "Sigma_factor_part", "Sigma_error"])

        for each_item in item_name_list:
            station_num = len(station_list)
            sn_num = len(sn_list)
            if FOMs_dict != {}:
                if each_item in FOMs_dict:
                    lower_limit = FOMs_dict[each_item]["Lower Limit"]
                    upper_limit = FOMs_dict[each_item]["Upper Limit"]
                    result = ''
                    repeatability, reproducibility, tolerance, sigma_part, sigma_factor, sigma_factor_part, sigma_error = \
                        self.get_GRR_result(each_item, station_num, sn_num, lower_limit, upper_limit, station_sn_data)
                    if tolerance < float(FOMs_dict[each_item]["PTR_THRESHOLD"]):
                        result = "pass"
                    else:
                        result = "Unacceptable"

                    GRR_excel.append([
                        each_item, lower_limit, upper_limit, repeatability, reproducibility, tolerance,
                        result, sigma_part, sigma_factor, sigma_factor_part, sigma_error
                    ])
                    # print("test item:", each_item)
                    # print("重复性:", repeatability, "再现性:", reproducibility, "toleranc:", tolerance,
                    #       "sigma_part:", sigma_part, "sigma_factor:", sigma_factor, "sigma_factor*part:",
                    #       sigma_factor_part,
                    #       "sigma_error:", sigma_error
                    #       )
            else:
                lower_limit = test_item_limit[each_item]["Lower Limit"]
                upper_limit = test_item_limit[each_item]["Upper Limit"]
                if lower_limit != "" and lower_limit != "NA" and upper_limit != "" and upper_limit != "NA":
                    repeatability, reproducibility, tolerance, sigma_part, sigma_factor, sigma_factor_part, sigma_error = \
                        self.get_GRR_result(each_item, station_num, sn_num, lower_limit, upper_limit, station_sn_data)

                    if tolerance > 0.3:
                        result = "Unacceptable"
                    else:
                        result = "pass"

                    GRR_excel.append([
                        each_item, lower_limit, upper_limit, repeatability, reproducibility, tolerance,
                        result, sigma_part, sigma_factor, sigma_factor_part, sigma_error
                    ])

                    # print("test item:", each_item)
                    # print("重复性:", repeatability, "再现性:", reproducibility, "toleranc:", tolerance,
                    #       "sigma_part:",sigma_part,"sigma_factor:",sigma_factor,"sigma_factor*part:",sigma_factor_part,
                    #       "sigma_error:",sigma_error
                    #      )

        self.write_GRR_excel(GRR_excel, FOMs_dict)



class Draw_picture_GUI:
    def __init__(self, csv_file_path_list, insight_csv_data):
        self.csv_file_path_list = csv_file_path_list
        if self.csv_file_path_list != "":
            # self.insight_csv_data = Insight_csv_data(self.csv_file_path_list)
            self.insight_csv_data = insight_csv_data

            self.current_item = [self.insight_csv_data.item_name_list[0]]
            self.current_item_name = self.insight_csv_data.item_name_list[0]
            self.current_select_xx = {}  # 每次刷新 xx_list_box 默认为全选
            self.color_dict = {}
            self.is_first_time_load_data = True
            self.is_finish_load_data = False
            self.is_close_GUI = False
            # 创建主界面
            self.root = tk.Toplevel(bg="white")
            self.ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(1)
            print("画图的缩放系数是", self.ScaleFactor)
            # self.root.tk.call('tk', 'scaling', self.ScaleFactor/72)

            self.root.title("draw picture tool")
            self.screenwidth = self.root.winfo_screenwidth()
            self.screenheight = self.root.winfo_screenheight()
            self.root.geometry('%sx%s' % (int(self.screenwidth), int(self.screenheight)))
            # 初始化GUI
            self.init_GUI()
            self.current_fig = BytesIO()
            self.draw_picture = Draw_picture(self)
            self.calculate_GRR = Calculate_GRR()
            # 派一个小弟去准备画图数据
            # 只要self.load_data_status值改变并且设置为1，即调用画图函数
            self.load_data_status = tk.IntVar()
            load_data_notification_CMD = lambda x, y, z: self.load_data_notification()
            self.load_data_status.trace_variable('w', load_data_notification_CMD)  # 绑定此变量到函数
            # 多线程加载全部数据
            init_insight_csv_data_threading = threading.Thread(target=self.load_data)
            init_insight_csv_data_threading.setDaemon(True)
            init_insight_csv_data_threading.start()
            self.root.mainloop()
        else:
            tk.messagebox.showinfo("Hi", "select a csv file first!")
            self.root.destroy()

    def generate_color(self, item_name_list, xx_list_dict):
        '''
        生成指定测项的颜色值
        color_dict = { "AC_CP":{
            "all_data": {"all_data":color1}
            "SerialNumber": {SN1:color1,SN2:color2,...}
            "Station ID": {}
            "Special Build Description":{}
            }
        }
        比较合适的颜色
        55, 80, 205
        10, 87, 218
        14, 91, 216
        self.color_dict["all_data"]["all_data"] = "#%02x%02x%02x" % (int(10), int(87), int(218))
        '''
        color_dict = {}
        for each_item in item_name_list:
            if each_item not in color_dict:
                color_dict[each_item] = {}
            for each_color_by in xx_list_dict[each_item]:
                if each_color_by not in color_dict[each_item]:
                    color_dict[each_item][each_color_by] = {}
                for each_xx in xx_list_dict[each_item][each_color_by]:
                    r = float(random.randint(1, 254) / 256)
                    g = float(random.randint(1, 254) / 256)
                    b = float(random.randint(1, 254) / 256)
                    color_tk = "#%02x%02x%02x" % (int(r * 256), int(g * 256), int(b * 256))

                    while (color_tk in color_dict[each_item][each_color_by].values()):  # 防止颜色重复，最多一共254*254*254种颜色
                        r = float(random.randint(1, 254) / 256)
                        g = float(random.randint(1, 254) / 256)
                        b = float(random.randint(1, 254) / 256)
                        color_tk = "#%02x%02x%02x" % (int(r * 256), int(g * 256), int(b * 256))
                    color_dict[each_item][each_color_by][each_xx] = color_tk
        return color_dict

    def show_picture(self):
        self.current_fig.seek(0)
        self.draw_picture.figure_point.savefig(self.current_fig)
        self.current_fig.seek(0)
        self.photo, image_size = change_photo(self.current_fig, int(self.screenwidth))
        self.figure_label.configure(image=self.photo)
        print("图片大小", image_size)

    def load_data_notification(self):
        if self.load_data_status.get() == 1:
            self.draw_picture.show_main_picture(self)  # 显示图片
            self.show_picture()
            # self.point_figure_canvas.draw()

    def merge_dict(self,original_dict,new_add_dict):
        result_dict = original_dict
        for each_key in new_add_dict:
            if each_key not in result_dict:
                result_dict[each_key] = new_add_dict[each_key]
        return result_dict

    def get_quene_data(self):
        """
        获取各个线程生成的数据
        """
        current_item_num = 1
        while True:
            if self.is_close_GUI:
                break
            try:
                if not self.load_data_quene.empty():
                    # [self.distinguish_data,self.xx_list_dict,self.station_sn_data]
                    result = self.load_data_quene.get()
                    print("收到多进程数据", result)
                    self.insight_csv_data.distinguish_data = self.merge_dict(self.insight_csv_data.distinguish_data,result[0])
                    self.insight_csv_data.xx_list_dict = self.merge_dict(self.insight_csv_data.xx_list_dict,result[1])
                    self.insight_csv_data.station_sn_data = self.merge_dict(self.insight_csv_data.station_sn_data,result[2])
                    for each_key in result[0]:
                        if each_key not in self.insight_csv_data.current_finish_search_item:
                            self.insight_csv_data.current_finish_search_item.append(each_key)
                            # self.color_dict = self.merge_dict(self.color_dict, self.generate_color([each_key],
                            #                                                         self.insight_csv_data.xx_list_dict))
                    current_item_num += len(result[0])
                    self.item_name_label["text"] = f"{current_item_num}/{len(self.insight_csv_data.item_name_list[:])}"
                    self.progress_bar["value"] = current_item_num / len(self.insight_csv_data.item_name_list[:]) * 100
                if current_item_num == len(self.insight_csv_data.item_name_list[:]):
                    self.item_name_label["text"] = f"finished,{len(self.insight_csv_data.current_finish_search_item)} item been loaded"
                    self.is_finish_load_data = True
                    break
            except Exception as e:
                print(e)
                break
            sleep(0.01)

    def load_picture_data(self):
        """
        画图的步骤：
            加载当前选择测试项的数据
            生成颜色空间
            刷新listbox
            画图
        如果只选择一个测项，颜色空间不变
        """
        start_time = time.time()
        for index, each_item in enumerate(self.current_item):
            if each_item not in self.insight_csv_data.current_finish_search_item:
                [distinguish_data, xx_list_dict,station_sn_data] = self.insight_csv_data.search_item_data_with_progress(
                                            [each_item],self.current_item_name_label,self.current_item_progress_bar)
                self.insight_csv_data.distinguish_data = self.merge_dict(self.insight_csv_data.distinguish_data,distinguish_data)
                self.insight_csv_data.xx_list_dict = self.merge_dict(self.insight_csv_data.xx_list_dict,
                                                                         xx_list_dict)
                self.insight_csv_data.station_sn_data = self.merge_dict(self.insight_csv_data.station_sn_data,
                                                                         station_sn_data)
            if index==0:  # 单个测项，颜色不变
                if self.color_dict:
                    for last_item in self.color_dict:
                        self.color_dict[each_item] = self.color_dict[last_item]
                        break
                else:
                    self.color_dict = self.generate_color([each_item],self.insight_csv_data.xx_list_dict)
            else:
                self.color_dict.update(self.generate_color([each_item], self.insight_csv_data.xx_list_dict))
        self.reflesh_xx_list_box(self.insight_csv_data.xx_list_dict)
        end_time = time.time()
        return end_time - start_time

    def load_data(self):
        """
        先显示当前选项的图
        如果第一次调用此函数，则加载全部画图数据
        """
        self.load_data_status.set(0)
        spend_time = self.load_picture_data()
        self.load_data_status.set(1)
        if self.is_first_time_load_data:
            self.is_first_time_load_data = False
            reflesh_xx_list_box_CMD = lambda x, y, z: self.reflesh_xx_list_box(self.insight_csv_data.xx_list_dict)
            self.color_by_string_var.trace_variable('w', reflesh_xx_list_box_CMD)  # 绑定此变量到函数
            # 开启多进程加载数据
            if spend_time*15*3<180:  # 总时间小于120秒才加载全部数据, 这里的时间是实际测试出来的，并不非常准确
                # self.insight_csv_data.start_load_picture_data()
                # 读取多进程数据
                self.load_data_quene = self.insight_csv_data.load_data_quene
                self.get_quene_data_threading = threading.Thread(target=self.get_quene_data)
                self.get_quene_data_threading.setDaemon(True)
                self.get_quene_data_threading.start()
            else:
                self.item_name_label["text"] = "the data size is too large, stop load data and som function can't use!"

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #               以下为界面显示
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def init_GUI(self):
        self.init_GUI_frame()
        self.place_frame_item_list()
        self.place_frame_input_detail()
        self.place_frame_title_entry()
        self.place_frame_title_button()
        self.bind_event()
        self.place_fram_load_data_progress()
        close_GUI_CMD = lambda: self.close_GUI()
        self.root.protocol('WM_DELETE_WINDOW', close_GUI_CMD)

    def init_GUI_frame(self):
        # 创建框架
        self.root.rowconfigure(3, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.frame_item_list = tk.Frame(self.root)  # , bg="CornflowerBlue"
        self.frame_item_list.grid(row=0, column=0, padx=10, sticky="we")
        self.frame_input_detail = tk.Frame(self.root)
        self.frame_input_detail.grid(row=0, column=1, padx=2, sticky="wens")

        self.root.columnconfigure(1, weight=1)
        self.frame_title_button = tk.Frame(self.root)
        self.frame_title_button.grid(row=1, column=0, columnspan=2, padx=10, sticky="we")
        self.frame_title_entry = tk.Frame(self.root)
        self.frame_title_entry.grid(row=2, column=0, columnspan=2, padx=10, sticky="we")

        self.frame_canvas = tk.Frame(self.root, padx=2)
        self.frame_canvas.grid(row=3, column=0, columnspan=2, sticky="wens")

        # self.point_figure_canvas = FigureCanvasTkAgg(self.draw_picture.figure_point, master=self.frame_canvas)
        # self.point_figure_canvas.get_tk_widget().grid(row=1, column=0, padx=3, sticky="wn")
        self.figure_label = tk.Label(self.frame_canvas)
        self.figure_label.pack(fill="both")
        self.figure_label.update()

        # self.toolbar = NavigationToolbar2Tk(self.point_figure_canvas, self.frame_canvas, pack_toolbar=False)
        # self.toolbar.update()
        # self.toolbar.grid(row=0, column=0, padx=3, sticky="wn")

        self.frame_load_data_progress = tk.Frame(self.root)  # , bg="CornflowerBlue"
        self.frame_load_data_progress.grid(row=4, column=0, columnspan=2, padx=10, sticky="we")


    # ------------------ item框架 ----------------------
    def show_item_list(self, item_name_list):
        self.item_name_list_box.delete(0, tk.END)
        item_index = 0
        for each_item in item_name_list:
            self.item_name_list_box.insert(tk.END, '  ' + str(item_index) + ". " + each_item)
            item_index += 1

    def change_current_item_name(self, each_item):
        if len(self.current_item) == 1:
            return ""
        else:
            if len(each_item) > 14:
                return each_item[:7] + "..." + each_item[-7:]
            else:
                return each_item

    def reflesh_xx_list_box(self, xx_list_dict):
        """
        self.current_select_xx = {'AC_CP': ['SN1',"SN2"...], 'Crown_Force_After_Engagement': ["SN1","SN2"...]}
        """
        self.xx_list_box.delete(0, tk.END)
        i = 0
        current_color_by = self.color_by_string_var.get()
        for each_item in self.current_item:
            self.current_select_xx[each_item] = xx_list_dict[each_item][current_color_by]
            if i==0:
                self.xx_list_box_select = tuple([i for i in range(len(xx_list_dict[each_item][current_color_by]))])
            item_name = self.change_current_item_name(each_item)
            for each_xx in xx_list_dict[each_item][current_color_by]:
                self.xx_list_box.insert(i, item_name + " " + each_xx)
                self.xx_list_box.itemconfigure(i, bg=self.color_dict[each_item][current_color_by][each_xx],
                                               selectbackground=self.color_dict[each_item][current_color_by][each_xx],
                                               selectforeground="white")
                i += 1

    def place_frame_item_list(self):
        # 文件位置 显示框
        self.file_path_entry = tk.Entry(self.frame_item_list, width=49)
        self.file_path_entry.grid(row=0, column=0, pady=2)
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, self.csv_file_path_list)
        # 测试项列表框
        self.item_name_list_box = tk.Listbox(self.frame_item_list, selectmode="extended", width=50,
                                             height=15)  # setgrid=True
        self.item_name_list_box.grid(row=1, column=0, pady=2, sticky="wns")
        self.show_item_list(self.insight_csv_data.item_name_list)
        # 测试项滚动条
        self.item_name_sb_ver = tk.Scrollbar(self.frame_item_list, orient="vertical")
        self.item_name_sb_ver.grid(row=1, column=1, pady=2, sticky="wns")
        self.item_name_sb_ver.configure(command=self.item_name_list_box.yview)  # 配置垂直滚动条
        self.item_name_list_box.config(yscrollcommand=self.item_name_sb_ver.set)  # xscrollcommand=sb_bottom.set
        # 筛选数据列表框
        # self.color_by_label = tk.Label(self.frame_item_list, text="color by:")
        # self.color_by_label.grid(row=0, column=2, sticky='w', pady=2)
        self.color_by_string_var = tk.StringVar()
        self.color_by_string_var.set(self.insight_csv_data.color_by_list[0])
        # self.color_by_menu = ttk.OptionMenu(self.frame_item_list, self.color_by_string_var,
        #                                     self.insight_csv_data.color_by_list[0], *self.insight_csv_data.color_by_list)
        self.color_by_menu = tk.OptionMenu(self.frame_item_list, self.color_by_string_var,
                                            *self.insight_csv_data.color_by_list)
        self.color_by_menu.grid(row=0, column=2, sticky='w', pady=2)

        # SN/Station ID/config 列表框
        self.xx_list_box = tk.Listbox(self.frame_item_list, selectmode="extended", width=35, height=13)
        self.xx_list_box.grid(row=1, column=2, pady=2, sticky="wens")

        # SN/Station ID/config 滚动条
        self.xx_sb_ver = tk.Scrollbar(self.frame_item_list, orient="vertical")
        self.xx_sb_ver.grid(row=1, column=3, pady=2, sticky="wns")
        self.xx_sb_ver.configure(command=self.xx_list_box.yview)  # 配置垂直滚动条
        self.xx_list_box.config(yscrollcommand=self.xx_sb_ver.set)


    def insert_input_detail_to_tree(self, item_name_list, input_detail_data, sn_list,station_id_list):
        input_detail_csv = []
        input_detail_csv.append(["SN"] + station_id_list)

        for each_SN in sn_list:
            each_tree_line = []
            each_tree_line.append(each_SN)
            for each_station in station_id_list:
                if each_station in input_detail_data.keys():
                    if each_SN in input_detail_data[each_station].keys():
                        input_station_SN_data = str(input_detail_data[each_station][each_SN + "_fail"]) + "F/" + \
                                                str(input_detail_data[each_station][each_SN]) + "T"
                    else:
                        input_station_SN_data = "NA"
                    each_tree_line.append(input_station_SN_data)
            self.input_tree.insert('', 'end', values=each_tree_line)
            input_detail_csv.append(each_tree_line)

        input_detail_list_sum = []
        input_detail_list_sum.append("sum")
        for each_station in station_id_list:
            input_station_SN_data = str(input_detail_data[each_station + "_fail_sum"]) + "F/" + \
                                    str(input_detail_data[each_station + "_sum"]) + "T"
            input_detail_list_sum.append(input_station_SN_data)
        self.input_tree.insert('', 'end', values=input_detail_list_sum)
        input_detail_csv.append(input_detail_list_sum)

        input_station_SN_data = str(input_detail_data["total_fail"]) + "F/" + \
                                str(input_detail_data["total_input"]) + "T"
        input_detail_list_sum = ["total", input_station_SN_data]
        self.input_tree.insert('', 'end', values=input_detail_list_sum)
        input_detail_csv.append(input_detail_list_sum)
        return input_detail_csv

    def save_input_data(self, input_detail_csv):
        if input_detail_csv != []:
            save_path = tkfile.asksaveasfilename(title="choose save path", defaultextension=".xls")
            haimeng_xlwt = Haimeng_xlwt(save_path)
            sheet = haimeng_xlwt.xls_book.add_sheet("Input_data")
            row = 0
            for each_line in input_detail_csv:
                if row == 0:
                    haimeng_xlwt.write_line(sheet, row, 0, each_line, haimeng_xlwt.gray_title_style)
                else:
                    haimeng_xlwt.write_line(sheet, row, 0, each_line, haimeng_xlwt.normal_style)
                row += 1
            haimeng_xlwt.xls_book.save(save_path)
        else:
            tk.messagebox.showinfo("Hi", "no data found")


    # ------------------ input 表格框架 ----------------------
    def place_frame_input_detail(self):
        input_frame_button = tk.Frame(self.frame_input_detail)
        input_frame_button.pack(side="top", fill="both",anchor="w", pady=5)
        style = ttk.Style()
        style.theme_use("clam")

        input_detail_list_title = ["SN"] + self.insight_csv_data.station_id_list
        style.configure("my.Treeview", background="LightGrey", foreground="black")  # fieldbackground="yellow",
        self.input_tree = ttk.Treeview(self.frame_input_detail, columns=input_detail_list_title,
                                       show='headings', style="my.Treeview", height=11)
        self.input_tree.pack(expand=True, fill="both")

        sb_treex = tk.Scrollbar(self.input_tree, orient="horizontal")
        sb_treex.pack(side="bottom", fill="x")  # grid 方法无法滚动，不知道为什么
        sb_treex.configure(command=self.input_tree.xview)  # 配置滚动条
        self.input_tree.config(xscrollcommand=sb_treex.set)  # xscrollcommand

        sb_treey = tk.Scrollbar(self.input_tree, orient="vertical")
        sb_treey.pack(side="right", fill="y")
        sb_treey.configure(command=self.input_tree.yview)  # 配置滚动条
        self.input_tree.config(yscrollcommand=sb_treey.set)
        # 显示标题
        for each_station in input_detail_list_title:
            self.input_tree.column(each_station, width=160, anchor='center', stretch=False)  # 自定义列宽的
            self.input_tree.heading(each_station, text=each_station)
        # 显示内容 并添加保存功能

        input_detail_csv = self.insert_input_detail_to_tree(self.insight_csv_data.item_name_list,
                                                            self.insight_csv_data.input_detail_data,
                                                            self.insight_csv_data.sn_list,
                                                            self.insight_csv_data.station_id_list
                                                            )

        # -----------------   创建 生成GRR 数据 按钮--------------------
        tk.Label(input_frame_button, text="Test times:").grid(row=0, column=3)
        self.generate_GRR_times = tk.StringVar()
        times_entry = tk.Entry(input_frame_button, textvariable=self.generate_GRR_times, width=5)
        times_entry.grid(row=0, column=4)

        tk.Label(input_frame_button, text="Slot_name/index:").grid(row=0, column=5)
        self.generate_GRR_data_slot = tk.StringVar()
        slot_entry = tk.Entry(input_frame_button, textvariable=self.generate_GRR_data_slot, width=5)
        slot_entry.grid(row=0, column=6)

        save_input_data_CMD = lambda: self.save_input_data(input_detail_csv)
        save_button = tk.Button(input_frame_button, text="save_data", command=save_input_data_CMD, width=10)
        save_button.grid(row=0, column=0)
        # todo no this function
        generate_GRR_data_CMD = lambda: self.calculate_GRR.generate_GRR_data(self.insight_csv_data.csv_list,
                                                        self.generate_GRR_times.get(),self.generate_GRR_data_slot.get())
        generate_GRR_data_button = tk.Button(input_frame_button, text="Generate GRR data:",
                                             command=generate_GRR_data_CMD, width=16)
        generate_GRR_data_button.grid(row=0, column=1, padx=2)


    # ------------------ entry 框架 ----------------------
    def create_entry(self, row_title, column_title, frame, label_name):
        tk.Label(frame, text=label_name).grid(row=row_title, column=column_title, sticky="w")
        column_title += 1
        entry = tk.Entry(frame, width=4)
        entry.grid(row=row_title, column=column_title, sticky="w")
        column_title += 1
        return row_title, column_title, entry

    def place_frame_title_entry(self):
        row_title = 0
        column_title = 0
        # 创建limit...输入框
        row_title, column_title, self.minimum_entry = self.create_entry(row_title, column_title, self.frame_title_entry,
                                                                        "Minimum")
        row_title, column_title, self.vertical_line_entry = self.create_entry(row_title, column_title,
                                                                              self.frame_title_entry, "Vertical_line")
        row_title, column_title, self.lower_limit_entry = self.create_entry(row_title, column_title,
                                                                            self.frame_title_entry, "Lower limit")
        row_title, column_title, self.upper_limit_entry = self.create_entry(row_title, column_title,
                                                                            self.frame_title_entry, "Upper limit")
        # -------------------- 勾选框 --------------------
        # 画图模式
        self.draw_picture_mode = {"X axis is time": tk.IntVar(), "bar no filled": tk.IntVar(), "Is normed": tk.IntVar(),
                                  "remove_invalid": tk.IntVar(), "Remove limit": tk.IntVar(), "Box image": tk.IntVar()}
        for each_mode in self.draw_picture_mode.keys():
            tk.Checkbutton(self.frame_title_entry, text=each_mode,
                           variable=self.draw_picture_mode[each_mode]).grid(row=row_title, column=column_title,
                                                                            sticky="w")
            column_title += 1

    # ------------------ 按钮 ----------------------
    def place_frame_title_button(self):

        # 创建设置按钮
        button_name_list = ["Load csv", "Save this image", "Save all item",
                            "Legend position", "Larger dot", "Smaller dot", "Change color", "break_down",
                            "run_GRR_report", "save all fail rate"]

        choose_csv_CMD = lambda: self.choose_csv()
        save_this_image_CMD = lambda: self.save_this_image()
        save_all_item_CMD = lambda: self.save_all_item()
        change_legend_location_CMD = lambda: self.change_legend_location()
        zoom_out_point_CMD = lambda: self.zoom_out_point()
        zoom_in_point_CMD = lambda: self.zoom_in_point()
        change_color_CMD = lambda: self.change_color()
        break_down_figure_CMD = lambda: self.break_down_figure()
        run_GRR_report_CMD = lambda: self.run_GRR_report()
        save_all_fail_rate_CMD = lambda: self.save_all_fail_rate()

        command_list = [choose_csv_CMD, save_this_image_CMD, save_all_item_CMD,
                        change_legend_location_CMD, zoom_out_point_CMD, zoom_in_point_CMD,
                        change_color_CMD, break_down_figure_CMD, run_GRR_report_CMD, save_all_fail_rate_CMD]
        row_title, column_title = 0, 0
        for each_button in range(len(button_name_list)):
            pad_x = 0
            if each_button == 8:
                foreground = "blue"
            else:
                foreground = "black"
            tk.Button(self.frame_title_button, text=button_name_list[each_button],
                      command=command_list[each_button],
                      foreground=foreground,
                      width=12).grid(row=row_title, column=column_title, padx=pad_x, pady=2, sticky="w")
            column_title += 1

    # ------------------ 事件  ----------------------
    def bind_event(self):
        # ---------  开始绑定刷新图片 -----------
        click_item_name_FUN = lambda event: self.click_item_name(event)
        self.item_name_list_box.bind("<ButtonRelease-1>", click_item_name_FUN)
        self.item_name_list_box.bind("<KeyRelease-Up>", click_item_name_FUN)
        self.item_name_list_box.bind("<KeyRelease-Down>", click_item_name_FUN)

        click_xx_list_box_FUN = lambda event: self.click_xx_list_box(event)
        self.xx_list_box.bind("<ButtonRelease-1>", click_xx_list_box_FUN)
        self.xx_list_box.bind("<KeyRelease-Up>", click_xx_list_box_FUN)
        self.xx_list_box.bind("<KeyRelease-Down>", click_xx_list_box_FUN)
        self.xx_list_box.bind("<KeyRelease-Escape>", click_xx_list_box_FUN)

        self.minimum_entry.bind("<KeyRelease-Return>", click_item_name_FUN)
        self.vertical_line_entry.bind("<KeyRelease-Return>", click_item_name_FUN)
        self.lower_limit_entry.bind("<KeyRelease-Return>", click_item_name_FUN)
        self.upper_limit_entry.bind("<KeyRelease-Return>", click_item_name_FUN)

    # ------------------ 底部进度条 ----------------------
    def place_fram_load_data_progress(self):
        tk.Label(self.frame_load_data_progress,text="Load all data:").grid(row=0,column=0)
        style = ttk.Style()
        style.configure("TProgressbar", foreground="blue", background="blue")
        self.item_name_label = tk.Label(self.frame_load_data_progress,text="start")
        self.item_name_label.grid(row=0,column=1)
        self.progress_bar = ttk.Progressbar(self.frame_load_data_progress, maximum=100, value=0, style="TProgressbar")
        self.progress_bar.grid(row=0, column=2, sticky="w", padx=5)

        self.current_item_name_label = tk.Label(self.frame_load_data_progress, text="NA")
        self.current_item_name_label.grid(row=0, column=3,padx=5)
        self.current_item_progress_bar = ttk.Progressbar(self.frame_load_data_progress,
                                                         maximum=100, value=0, style="TProgressbar")
        self.current_item_progress_bar.grid(row=0, column=4, sticky="w",padx=5)




# ----------------   事件函数 ----------------------
    def close_GUI(self):
        self.is_close_GUI = True
        time.sleep(0.5)
        for each_process in self.insight_csv_data.load_data_process_list:
            try:
                each_process.terminate() # 关闭加载数据进程
            except Exception as e:
                print(f"删除进程失败:{e}")
        self.root.destroy()

    def choose_csv(self):
        self.csv_file_path_list = tkfile.askopenfilenames(title="选择 单个或多个 csv数据 文件")
        if self.csv_file_path_list != "":
            self.close_GUI()
            self.__init__(self.csv_file_path_list)

    def save_this_image(self,is_show_message=True):
        folder_name = self.color_by_string_var.get()
        dir_path = os.path.dirname(self.csv_file_path_list[0]) + "/" + folder_name
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        save_path = dir_path + '/' + self.current_item_name + '.png'
        self.draw_picture.figure_point.savefig(save_path, bbox_inches='tight')  # 保存图片
        if is_show_message:
            tk.messagebox.showinfo("Hi", "Result have been save at %s"%(save_path))

    def create_progressbar(self):
        tk.Label(self.frame_load_data_progress,text="saving the date, don't operate").grid(row=0,column=5)
        progressbar = ttk.Progressbar(self.frame_load_data_progress, maximum=100, value=0, style="TProgressbar")
        #progressbar.pack(fill="x", expand=True)
        progressbar.grid(row=0,column=6,sticky="we")
        label = tk.Label(self.frame_load_data_progress,text="0/0")
        #label.pack(side = "bottom")
        label.grid(row=0,column=7)
        return progressbar,label

    def save_all_item_process_fun(self):
        progressbar,label = self.create_progressbar()
        for each_item in self.insight_csv_data.item_name_list:
            # 如果没数据，先导入数据
            if each_item not in self.insight_csv_data.current_finish_search_item:
                self.load_picture_data()
            if self.is_close_GUI:
                return None
            try:
                self.current_item = [each_item]
                self.current_item_name = self.get_title()
                self.draw_picture.show_main_picture(self)  # 显示图片
                self.save_this_image(False)
                progressbar["value"] = self.insight_csv_data.item_name_list.index(each_item) / len(self.insight_csv_data.item_name_list) * 100
                label["text"] = "%s %s/%s"%(each_item,self.insight_csv_data.item_name_list.index(each_item),len(self.insight_csv_data.item_name_list))
            except Exception as e:
                print("出错啦",e)
                break
            sleep(0.1)
        label["text"] = "save finished"

    def save_all_item(self):
        save_all_item_process = threading.Thread(target=self.save_all_item_process_fun)
        save_all_item_process.setDaemon(True)
        save_all_item_process.start()

    def zoom_in_point(self):
        if self.draw_picture.point_size > 1 and self.draw_picture.line_size > 1:
            self.draw_picture.point_size -= 1
            self.draw_picture.line_size -= 1
        self.draw_picture.show_main_picture(self)  # 显示图片
        # self.point_figure_canvas.draw()
        self.show_picture()

    def zoom_out_point(self):
        if self.draw_picture.point_size < 20 and self.draw_picture.line_size < 10:
            self.draw_picture.point_size += 1
            self.draw_picture.line_size += 1
        self.draw_picture.show_main_picture(self)  # 显示图片
        # self.point_figure_canvas.draw()
        self.show_picture()

    def change_legend_location(self):
        current_index = self.draw_picture.legend_location_list.index(self.draw_picture.legend_location)
        if current_index == len(self.draw_picture.legend_location_list) - 1:
            current_index = 0
        else:
            current_index += 1
        self.draw_picture.legend_location = self.draw_picture.legend_location_list[current_index]
        self.draw_picture.show_main_picture(self)  # 显示图片
        # self.point_figure_canvas.draw()
        self.show_picture()

    def get_current_item(self, item_name_list):
        self.item_name_list_box_select = self.item_name_list_box.curselection()
        if self.item_name_list_box_select != ():
            current_item = []
            for each_item in self.item_name_list_box_select:
                current_item.append(item_name_list[each_item])
                self.current_item = current_item
        else:
            # item_index = 0
            current_item = self.current_item
        return current_item

    def get_title(self):
        title = ""
        for each_item in self.current_item:
            item_name = self.change_current_item_name(each_item)
            if item_name == "":
                item_name = each_item
            title += str(item_name) + " & "
        if len(title) > 50:
            title = title[:50] + "..."
        else:
            title = title[:-2]
        return title

    def click_item_name2(self):
        self.current_item = self.get_current_item(self.insight_csv_data.item_name_list)
        self.current_item_name = self.get_title()
        init_insight_csv_data_threading = threading.Thread(target=self.load_data)
        init_insight_csv_data_threading.setDaemon(True)
        init_insight_csv_data_threading.start()

    def click_item_name(self, event):
        self.current_item = self.get_current_item(self.insight_csv_data.item_name_list)
        self.current_item_name = self.get_title()
        init_insight_csv_data_threading = threading.Thread(target=self.load_data)
        init_insight_csv_data_threading.setDaemon(True)
        init_insight_csv_data_threading.start()

    def get_current_xx(self):
        # current_xx_list = [{"AC_CP":[]},{...}] 当前list_box的所有项目列表
        current_xx_list = []
        current_color_by = self.color_by_string_var.get()
        for each_item in self.current_item:
            current_xx_list.append({each_item: self.insight_csv_data.xx_list_dict[each_item][current_color_by]})

        current_select_xx = {}  # 当前选择的项
        # 获取当前选中项
        if self.xx_list_box.curselection() != ():  # 有选择项
            self.xx_list_box_select = self.xx_list_box.curselection() # 如果当前有选择项，则更新变量，如果没有选择，则保留上一次的选项，用于多进程
        if self.xx_list_box_select!=():
            for each_select in self.xx_list_box_select:
                i = 0
                for each_xx in current_xx_list:
                    for each_name in each_xx:
                        name = each_name
                    if each_select > i + len(each_xx[name]) - 1:
                        i += len(each_xx[name])
                    else:
                        if name not in current_select_xx:
                            current_select_xx[name] = []
                        current_select_xx[name].append(each_xx[name][each_select - i])
                        break
            self.current_select_xx = current_select_xx
        else:  # 没有选择项
            current_select_xx = self.current_select_xx
        return current_select_xx

    def click_xx_list_box(self, event):
        self.current_select_xx = self.get_current_xx()
        self.draw_picture.show_main_picture(self)  # 显示图片
        # self.point_figure_canvas.draw()
        self.show_picture()

    def change_color(self):
        new_color_dict = self.generate_color(self.current_item, self.insight_csv_data.xx_list_dict)
        for each_item in self.current_item:
            self.color_dict[each_item] = new_color_dict[each_item]

        self.reflesh_xx_list_box(self.insight_csv_data.xx_list_dict)
        self.draw_picture.show_main_picture(self)  # 显示图片
        # self.point_figure_canvas.draw()
        self.show_picture()

    def save_all_fail_rate(self):
        #if len(self.insight_csv_data.current_finish_search_item)<len(self.insight_csv_data.item_name_list):
        if not self.is_finish_load_data:
            tkmessage.showinfo("Hi", "still loading data, please wait.")
        else:
            save_path = tkfile.asksaveasfilename(title="choose save path", defaultextension=".xls")
            haimeng_xlwt = Haimeng_xlwt(save_path)
            sheet = haimeng_xlwt.xls_book.add_sheet("Fail data")

            title = ["item","total test","fail","fail rate","limit"]
            haimeng_xlwt.write_line(sheet,0,0,title,haimeng_xlwt.gray_title_style)
            sheet.col(0).width = 15000
            row=1
            for each_item in self.insight_csv_data.distinguish_data:
                total_test,fail_num = 0,0
                limit = "["+self.insight_csv_data.test_item_limit[each_item]["Upper Limit"]+","+self.insight_csv_data.test_item_limit[each_item]["Lower Limit"]+"]"
                for each_xx in self.insight_csv_data.xx_list_dict[each_item][self.color_by_string_var.get()]:
                    total_test += self.insight_csv_data.distinguish_data[each_item][self.color_by_string_var.get()][each_xx]["total test"]
                    fail_num += self.insight_csv_data.distinguish_data[each_item][self.color_by_string_var.get()][each_xx]["fail num"]
                if total_test==0:
                    fail_rate = "0.0%"
                else:
                    fail_rate = "%.2f"%(100*fail_num/total_test) +"%"
                line = [each_item,str(total_test),str(fail_num),fail_rate,limit]
                haimeng_xlwt.write_line(sheet,row,0,line,haimeng_xlwt.normal_style)
                row+=1
            haimeng_xlwt.xls_book.save(save_path)

    def break_down_figure(self):
        self.draw_picture.reflesh_Draw_picture_GUI(self)
        self.draw_picture.break_down_figure()

    def run_GRR_report(self):
        self.calculate_GRR.run_GRR_report(self.insight_csv_data.csv_list,self.generate_GRR_times.get(),
                                          self.generate_GRR_data_slot.get())

    # def change_time_tuple(self, time):
    #     time_re = re.search(r'^(\d{4}).(\d+).(\d+).(\d+):(\d+):*(\d*)', time)
    #     return (
    #         time_re.group(1), time_re.group(2), time_re.group(3), time_re.group(4), time_re.group(5), time_re.group(6))
    #
    # def is_time(self, string):
    #     # 目前只识别：2021-10-01 10:08:09, 2021-10-01 10:08, 2021/10/01 10:08:09, 2021/10/01 10:08 四种类型
    #     time_re = re.search(r'^(\d{4}).(\d+).(\d+).(\d+):(\d+):*(\d*)', string)
    #     if time_re != None:
    #         return True
    #     else:
    #         return False
    #
    # def compare_test_time(self, new_csv_time, old_csv_time):
    #     new_max = old_csv_time
    #     if '-' in new_csv_time:
    #
    #         if not self.is_time(new_csv_time) or not self.is_time(old_csv_time):
    #             print("Hi", "compare test time error,cause time format error")
    #             return None
    #         else:
    #             time_new = self.change_time_tuple(new_csv_time)
    #             time_max_old = self.change_time_tuple(old_csv_time)
    #             for each_new in range(len(time_new)):
    #                 if time_new[each_new] > time_max_old[each_new]:
    #                     return True
    #                 elif time_new[each_new] < time_max_old[each_new]:
    #                     return False
    #                 else:
    #                     continue
    #             return True  # 两个值相等








class Draw_picture:
    def __init__(self, Draw_picture_GUI):
        #  ------------   画图初始化 ------------------
        self.Draw_picture_GUI = Draw_picture_GUI
        Draw_picture_GUI.root.update()
        self.screenwidth = Draw_picture_GUI.root.winfo_width()
        self.screenheight = Draw_picture_GUI.screenheight
        Draw_picture_GUI.frame_canvas.update()
        figure_height = Draw_picture_GUI.frame_canvas.winfo_height()
        print("图片框架高度", figure_height)
        dpi = 200
        picture_width = self.screenwidth/100
        picture_height = self.screenheight/100*figure_height/self.screenheight
        figsize = (picture_width, picture_height)
        print("画布尺寸是", figsize)
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        self.figure_point, axs = plt.subplots(nrows=1, ncols=2, dpi=dpi, figsize=figsize, facecolor="LightGrey")  #figsize=(14.5, 4.15)
        self.ax1_point = axs[0]
        self.ax2_point = axs[1]

        self.point_size = 3
        self.line_size = 1
        self.legend_location_list = ["best", "lower right", "lower left", "upper left", "upper right", None]
        self.legend_location = self.legend_location_list[0]
        self.is_show_break_down = False

    def close_break_down(self):
        self.is_show_break_down = False
        self.break_down_root.destroy()

    def show_break_down_picture(self):
        self.current_break_down_fig.seek(0)
        self.figure_break_down.savefig(self.current_break_down_fig)
        self.current_break_down_fig.seek(0)
        self.photo, image_size = change_photo(self.current_break_down_fig, self.break_down_GUI_width)
        self.break_down_label.configure(image=self.photo)

    def draw_break_down_figure_GUI(self):
        self.is_show_break_down = True
        self.break_down_root = tk.Toplevel(bg="LightGrey")  # 创建主界面
        self.break_down_root.title("break_down_figure")  # 主界面名字
        self.break_down_GUI_width = int(self.screenwidth * 0.8)
        self.break_down_GUI_height = int(self.screenheight * 0.8)
        self.break_down_root.geometry(f'{self.break_down_GUI_width}x{self.break_down_GUI_height}')  # 主界面大小
        frame_break_down_canvas = tk.Frame(self.break_down_root)
        frame_break_down_canvas.grid(row=0, column=0, sticky="wens")
        # self.break_down_canvas = FigureCanvasTkAgg(self.figure_break_down, master=frame_break_down_canvas)
        # self.break_down_canvas.get_tk_widget().grid(row=0, column=0, sticky="wens")
        # self.break_down_canvas.draw()  # 将图片画到tk
        self.current_break_down_fig = BytesIO()
        self.break_down_label = tk.Label(frame_break_down_canvas)
        self.break_down_label.pack(fill="both")
        self.show_break_down_picture()
        # self.figure_point.plot()
        close_break_down_CMD = lambda: self.close_break_down()
        self.break_down_root.protocol('WM_DELETE_WINDOW', close_break_down_CMD)  # 重定义关闭窗口时的方法

    def draw_break_down_figure(self):
        figure_row = 4
        figure_column = 2
        if not self.is_show_break_down :
            self.figure_break_down, self.axs_break_down = plt.subplots(nrows=figure_row, ncols=figure_column, dpi=100,
                                                                  figsize=(14.2, 8),
                                                                  facecolor="LightGrey",
                                                                  edgecolor="red",
                                                                  sharey="all")  # ,sharex="all"
            self.draw_break_down_figure_GUI()

        item_name = self.current_item[0]
        unit, upper_limit, lower_limit = self.get_limit(item_name)

        # 清空画布
        for each_row in range(figure_row):
            for each_column in range(figure_column):
                self.axs_break_down[each_row][each_column].cla()
                if len(self.sn_list) > 5:
                    self.axs_break_down[each_row][each_column].tick_params(axis="x", labelrotation=30)  # 设置横轴标题旋转角度
                # 画上下限
                if not self.remove_limit_mode:
                    if lower_limit != "NA":
                        self.axs_break_down[each_row][each_column].axhline(float(lower_limit), linewidth=0.5,
                                                                      linestyle='--', color="red")  # 画下限
                    if upper_limit != "NA":
                        self.axs_break_down[each_row][each_column].axhline(float(upper_limit), linewidth=0.5,
                                                                      linestyle='--', color="red")
                self.axs_break_down[each_row][each_column].grid(color="black", which='major', axis='x', ls="dashed",
                                                           lw=0.5, alpha=0.7)
        for each_station in range(len(self.station_list)):
            station = self.station_list[each_station]
            # 检查当前是哪个图片
            if each_station < figure_row:
                current_column = 0
                current_row = each_station
            elif each_station >= figure_row and each_station < 8:
                current_column = 1
                current_row = each_station - figure_row
            else:
                tk.messagebox.showerror("Hi", "can't showed more than 10 stations")
                break

            # 给每张图片写station 名字
            br = self.axs_break_down[current_row][current_column].twinx()  # 右边添加轴
            if len(station) < 15:
                br.set_ylabel(station)
            else:
                br.set_ylabel(station[:15] + "\n" + station[15:])
            br.set_yticks([])  # 隐藏右边刻度显示

            # 修改测试项名称
            if each_station == 0 and current_column == 0:
                self.axs_break_down[current_row][current_column].set_title(item_name, loc="left", fontsize=12,color="MidnightBlue")

            # 画测试值
            y_value_list = []
            label_list = self.sn_list[:]
            label_list2 = [' '] * len(self.sn_list)
            for each_SN in range(len(self.sn_list)):
                SN = self.sn_list[each_SN]
                if SN in self.station_sn_data[item_name][station].keys():
                    y_value = self.station_sn_data[item_name][station][SN][:]
                    if self.remove_invalid_mode:
                        y_value = self.remove_invalid_data(y_value)
                    y_value_list.append(y_value)
                else:
                    y_value_list.append([])
            if current_row == len(self.station_list)-1 or current_row == 3:
                self.axs_break_down[current_row][current_column].boxplot(y_value_list, labels=label_list, sym='-',meanline=True)
            else:
                self.axs_break_down[current_row][current_column].boxplot(y_value_list, labels=label_list2, sym='-',meanline=True)

            self.axs_break_down[current_row][current_column].locator_params(axis='y', nbins=10)  # 横轴刻度数为20
            if self.minimum_entry_value != "":
                if self.is_float(self.minimum_entry_value):
                    axs_break_down[current_row][current_column].set_ylim(bottom=float(self.minimum_entry_value))

        self.figure_break_down.subplots_adjust(left=0.05, right=0.95, bottom=0.15, top=0.9, wspace=0.15, hspace=0.2)
        self.break_down_canvas.draw()
        if not self.is_show_break_down:
            self.is_show_break_down = True
            self.break_down_root.mainloop()

    def break_down_figure(self):
        self.sn_list = self.insight_csv_data.sn_list
        self.station_list = self.insight_csv_data.station_id_list
        self.station_sn_data = self.insight_csv_data.station_sn_data
        if len(self.current_item) > 1:
            tk.messagebox.showinfo("Hi", "can only select a test item")
        elif len(self.station_list)>8:
            tk.messagebox.showinfo("Hi", "not support more than 8 stations")
        elif len(self.sn_list)>10:
            tk.messagebox.showinfo("Hi", "not support more than 10 units")
        else:
            self.draw_break_down_figure()


    def change_time_format(self, time_list):
        x_values = []
        current_date = None
        for each_time in time_list:
            try:
                if "-" in each_time:
                    if len(each_time) > 16:
                        current_date = datetime.strptime(each_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        current_date = datetime.strptime(each_time, "%Y-%m-%d %H:%M")
                if "/" in each_time:
                    if len(each_time) > 16:
                        current_date = datetime.strptime(each_time, "%Y/%m/%d %H:%M:%S")
                    else:
                        current_date = datetime.strptime(each_time, "%Y/%m/%d %H:%M")
                x_values.append(current_date)
            except:
                current_date = datetime.strptime('1999/07/07 00:00', "%Y/%m/%d %H:%M")
                x_values.append(current_date)
        return x_values

    def get_x_y_value_list(self, item_name):
        time_value_list, y_value_list = [], []
        for each_xx in self.current_select_xx[item_name]:
            time_value = self.insight_csv_data.distinguish_data[item_name][self.current_color_by][each_xx][
                             "time_value"][:]  # 用复制防止数据被更改
            if time_value != []:  # 不是insight导出的数据，时间为空
                time_value = self.change_time_format(time_value)
            time_value_list.append(time_value)
            y_value = self.insight_csv_data.distinguish_data[item_name][self.current_color_by][each_xx]["y_value"][:]
            y_value_list.append(y_value)
        return time_value_list, y_value_list

    def is_float(self, string):
        i = 0
        for each_s in string:
            i += 1
            if not each_s.isdigit() and each_s != ".":
                if i == 1:
                    if each_s == "-":
                        continue
                else:
                    return False
            else:
                return True

    def get_limit(self, item_name):
        upper_limit, lower_limit = "", ""
        unit = self.insight_csv_data.test_item_limit[item_name]["Measurement Unit"]
        if self.user_define_lower_limit != "":
            if self.is_float(self.user_define_lower_limit):
                lower_limit = self.user_define_lower_limit
            else:
                tk.messagebox.showinfo("Hi", "invalid input lower limit")
        else:
            lower_limit = self.insight_csv_data.test_item_limit[item_name]["Lower Limit"]

        if self.user_define_upper_limit != "":
            if self.is_float(self.user_define_upper_limit):
                upper_limit = self.user_define_upper_limit
            else:
                tk.messagebox.showinfo("Hi", "invalid input lower limit")
        else:
            upper_limit = self.insight_csv_data.test_item_limit[item_name]["Upper Limit"]
        return unit, upper_limit, lower_limit

    def is_a_larger_b(self, a, b):
        if self.is_float(a) and self.is_float(b):
            if float(a) > float(b):
                return True
            else:
                return False
        else:
            return False

    def get_unit(self, item_data):
        unit = ""
        for each_item in item_data:
            unit += item_data[each_item][0]+ " & "
        if len(unit) > 50:
            unit = unit[:50] + "..."
        else:
            unit = unit[:-2]
        return unit

    def remove_string_from_list(self, value_list):
        new_value_list = value_list[:]
        for each_value in value_list:
            if not self.is_float(str(each_value)):
                new_value_list.remove(each_value)
        return new_value_list

    def get_list_max_min(self, value_list):
        new_value_list = self.change_2D_1D_list(value_list)
        new_value_list = self.remove_string_from_list(new_value_list[:])
        if new_value_list != []:
            y_max = float(new_value_list[0])
            y_min = float(new_value_list[0])
            for each_value in new_value_list:
                if float(each_value) > y_max:
                    y_max = float(each_value)
                if float(each_value) < y_min:
                    y_min = float(each_value)
            return y_max, y_min
        else:
            return "", ""

    def get_cpk(self, y_value_list, lower_limit, upper_limit):
        new_y_value_list = []
        # Todo 判断维数
        for i in y_value_list:
            new_y_value_list += i
        new_y_value_list = self.remove_invalid_data(new_y_value_list)
        if len(new_y_value_list) > 0:
            max_value, min_value = self.get_list_max_min(new_y_value_list)
            max_value = "%.2f" % (max_value)
            min_value = "%.2f" % (min_value)
            mean_value = "%.2f" % (sum(new_y_value_list) / len(new_y_value_list))
            std_value = "%.3f" % (np.std(new_y_value_list))

            if upper_limit != "NA" and upper_limit != "" and float(std_value) != 0:
                cpu = "%.2f" % ((float(upper_limit) - float(mean_value)) / 3 / float(std_value))
            else:
                cpu = "NA"
            if lower_limit != "NA" and lower_limit != "" and float(std_value) != 0:
                cpl = "%.2f" % ((float(mean_value) - float(lower_limit)) / 3 / float(std_value))
            else:
                cpl = "NA"
            if cpu != "NA" and cpl != "NA":
                cpk = "%.2f" % (min(float(cpu), float(cpl)))
            else:
                cpk = "NA"
        else:
            max_value, min_value, mean_value, std_value, cpu, cpl, cpk = "NA", "NA", "NA", "NA", "NA", "NA", "NA"
        return max_value, min_value, mean_value, std_value, cpu, cpl, cpk

    def remove_invalid_data(self, y_values, x_values=None):
        new_y_values = y_values[:]
        new_x_values = None
        if x_values != None:
            new_x_values = x_values[:]
        while (0.000141747 in new_y_values):
            invalid_index = new_y_values.index(0.000141747)
            # print("我是索引",invalid_index)
            new_y_values.pop(invalid_index)
            # print("我是y",y_values,"还有x",x_values)
            if new_x_values != None:
                new_x_values.pop(invalid_index)
            # print("我是x",x_values)
        if new_x_values != None:
            return new_y_values, new_x_values
        else:
            return new_y_values

    def is_fail_value(self, measurement_value, upper_limit, lower_limit):
        if measurement_value != "" and measurement_value != 0.000141747:
            if upper_limit != "NA" and upper_limit != "":
                if float(measurement_value) > float(upper_limit):
                    return True
            if lower_limit != "NA" and lower_limit != "":
                if float(measurement_value) < float(lower_limit):
                    return True
            return False
        else:
            return False

    def change_2D_1D_list(self, value_list):
        new_value_list = []
        for i in value_list:
            try:
                new_value_list += i[:]
            except:
                new_value_list.append(i)
        return new_value_list

    def get_fail_rate(self, item_data):
        total_test = 0
        fail_num = 0
        for each_item in item_data:
            upper_limit, lower_limit, y_value_list = item_data[each_item][1], item_data[each_item][2], \
                                                     item_data[each_item][4]
            new_y_value_list = self.change_2D_1D_list(y_value_list)
            total_test += len(new_y_value_list)
            new_y_value_list = self.remove_invalid_data(new_y_value_list)
            for each_value in new_y_value_list:
                if self.is_fail_value(each_value, upper_limit, lower_limit):
                    fail_num += 1
        return total_test, fail_num

    def init_distinguish_picture(self, item_data, all_y_value_list, upper_limit, lower_limit):
        self.ax1_point.cla()
        self.ax2_point.cla()
        # -------------------------- 设置图片位置和网络图 -----------------
        self.ax1_point.set_position([0.06, 0.195, 0.44, 0.725])  # 坐标轴距离左边0.05，距离底部0.2，宽度0.45，高度0.75
        self.ax2_point.set_position([0.56, 0.205, 0.42, 0.725])  # 坐标轴距离左边0.05，距离底部0.2，宽度0.45，高度0.75
        # self.ax1_point.set_position([0.1, 0.3, 0.4, 0.6])  # 坐标轴距离左边0.05，距离底部0.2，宽度0.45，高度0.75
        # self.ax2_point.set_position([0.57, 0.3, 0.39, 0.6])  # 坐标轴距离左边0.05，距离底部0.2，宽度0.45，高度0.75
        self.ax2_point.grid(color="black", which='major', axis='both', ls="dashed", lw=0.5, alpha=0.5)


        # 获取标题
        ax1_title = self.current_item_name
        ax2_title = ax1_title
        unit = self.get_unit(item_data)

        # 获取轴标签
        max_value, min_value, mean_value, std_value, cpu, cpl, cpk = self.get_cpk(all_y_value_list, lower_limit,
                                                                                  upper_limit)
        cpk_str = 'lower:' + str(lower_limit) + ', upper:' + str(upper_limit) + ") " + "(Max:" + str(max_value) \
                  + ", Min:" + str(min_value) + ", \nMean:" + str(mean_value) + ", Std:" + str(std_value) \
                  + ", Cpu:" + str(cpu) + ", Cpl:" + str(cpl) + ", Cpk:" + str(cpk)
        # 获取测试数量
        total_test, fail_num = self.get_fail_rate(item_data)
        if total_test == 0:
            fail_rate = "0.0%"
        else:
            fail_rate = f"{100 * fail_num / total_test:.2%}"
        ax1_xlabel = "Total test:" + str(total_test) + "  " + "Fail:" + str(fail_num) + "  " + \
                     "Fail rate:" + fail_rate + "%"
        ax1_ylabel = "measure value/" + unit + '  (lower:' + str(lower_limit) + ', upper:' + str(upper_limit) + ")"
        ax2_xlabel = "measure value/" + unit + " (" + cpk_str + ")"
        ax2_ylabel = "Test count"

        # -----------  ax1 标题 设置 ------------
        self.ax1_point.set_xlabel(ax1_xlabel, fontsize=10, color="blue")
        self.ax1_point.set_ylabel(ax1_ylabel, fontsize=10, color="blue")  # 纵坐标名字设置
        self.ax1_point.set_title(ax1_title, fontsize=11, color="MidnightBlue")  # 设置标题名字
        # -----------  ax2 标题 设置 ------------
        self.ax2_point.set_xlabel(ax2_xlabel, fontsize=10, color="blue")
        self.ax2_point.set_ylabel(ax2_ylabel, fontsize=10, color="blue")
        self.ax2_point.set_title(ax2_title, fontsize=11, color="MidnightBlue")  # 设置标题名字

    def get_point_value(self, y_value, time_value):
        x_value = []
        ax1 = self.ax1_point
        if not self.x_axis_is_time_mode:
            if self.remove_invalid_mode:
                y_value = self.remove_invalid_data(y_value)  # 移除无效数据
        # 获取x轴 的值
        # 横轴为时间
        if self.x_axis_is_time_mode and time_value != []:  # 时间存在
            ax1.xaxis.set_major_formatter(mdate.DateFormatter('%y-%m-%d %H:%M'))
            ax1.tick_params(axis="x", labelrotation=30)  # 设置刻度标签角度
            # Todo 设置刻度数
            ax1.grid(color="black", which='major', axis='both', ls="dashed", lw=0.5, alpha=0.5)
            if self.remove_invalid_mode:
                y_value, x_value = self.remove_invalid_data(y_value, x_values=time_value)  # 移除无效数据
            else:
                x_value = time_value
        # 横轴为 次数
        elif not self.x_axis_is_time_mode:
            ax1.locator_params(axis='x', nbins=20)  # 横轴刻度数为20
            x_value = np.arange(len(y_value))
            ax1.grid(color="black", which='major', axis='both', ls="dashed", lw=0.5, alpha=0.5)
        return x_value, y_value

    def draw_point_hist_picture(self, i, each_item, item_name, y_value_list, x_value, y_value, ax2_xmax, ax2_xmin,
                                current_xx):
        if i <= 10:
            scatter_label = item_name + " " + current_xx  # item——name是转化缩短后的名字，each——item是真实名字
        else:
            scatter_label = None
        if self.bar_no_filled_mode or len(y_value_list) > 10:
            hist_type = 'step'
        else:
            hist_type = "bar"
        if self.is_normed_mode:
            is_normed = True
        else:
            is_normed = False
        # ----- 画散点图 ----------
        if not self.GRR_Image_mode:
            # ax1.scatter(x_values_list_1D, y_values_list_1D, c=color_list_1D, s=self.point_size)
            self.ax1_point.plot(x_value, y_value,
                                c=self.color_dict[each_item][self.current_color_by][current_xx],
                                marker="o",
                                markersize=self.point_size, linestyle="-", linewidth=0.3, label=scatter_label)
        # ------ 画直方图 --------
        tops, bins, Patch_list = self.ax2_point.hist(y_value, bins=50,
                                                     range=(ax2_xmin, ax2_xmax),
                                                     color=
                                                     self.color_dict[each_item][self.current_color_by][
                                                         current_xx],
                                                     density=is_normed,
                                                     histtype=hist_type,
                                                     linewidth=self.line_size,
                                                     stacked=True,
                                                     label=scatter_label)

    def draw_lengend(self, y_value_list):
        # ----------------- 画图例 --------------------------
        if len(y_value_list) < 5:
            legend_column = 1
        else:
            legend_column = 2
        if self.legend_location != None:
            if not self.GRR_Image_mode:
                self.ax1_point.legend(loc=self.legend_location, fontsize=6,
                                      ncol=legend_column)  # bbox_to_anchor=(1, 1.3)
            self.ax2_point.legend(loc=self.legend_location, fontsize=6, ncol=legend_column)

    def draw_normal_school(self, y_value_list, lower_limit, upper_limit):
        # -------------------------- 画正态分布图 -----------------
        max_value, min_value, mean_value, std_value, cpu, cpl, cpk = \
            self.get_cpk(y_value_list, lower_limit, upper_limit)
        y_value_list_1D = []
        for each_value in y_value_list:
            y_value_list_1D += each_value
        if min_value != "NA" and max_value != "NA" and mean_value != "NA" \
                and std_value != "NA" and self.is_normed_mode \
                and len(y_value_list_1D) > 1:
            x_value = np.linspace(float(min_value), float(max_value), 1000)
            kde = mlab.GaussianKDE(y_value_list_1D)  # 核密度曲线
            self.ax2_point.plot(x_value, kde(x_value), color="red", linewidth=1.5, linestyle="--")
            y_value = norm.pdf(x_value, float(mean_value), float(std_value))  # 正态分布曲线
            self.ax2_point.plot(x_value, y_value, color="green", linewidth=1.5, linestyle="--")

    def draw_limit(self, lower_limit, upper_limit, ax2_xmax):
        # -------------------------- 画折线图 -----------------
        if not self.remove_limit_mode:
            if lower_limit != "NA" and lower_limit != "":
                self.ax1_point.axhline(float(lower_limit), linewidth=1, linestyle='-', color="red")  # 画下限
                self.ax2_point.axvline(float(lower_limit), linewidth=1, linestyle='-', color="red")
            if upper_limit != "NA" and upper_limit != "":
                self.ax1_point.axhline(float(upper_limit), linewidth=1, linestyle='-', color="red")  # 画上限
                self.ax2_point.axvline(float(upper_limit), linewidth=1, linestyle='-', color="red")
        if self.vertical_line\
                != "":
            if self.is_float(self.vertical_line
                             ):
                self.ax1_point.axvline(float(self.vertical_line
                                             ), linewidth=1,
                                       linestyle='--', color="blue")  # 画竖线
                if upper_limit != "NA" and upper_limit != "":
                    if float(ax2_xmax) > float(upper_limit):
                        y_mark = float(ax2_xmax) * 1
                    else:
                        y_mark = float(upper_limit) * 1
                else:
                    y_mark = float(ax2_xmax) * 1
                self.ax1_point.text(x=float(self.vertical_line
                                            ), y=float(y_mark),
                                    s=r"$%s$" % (self.vertical_line
                                                 ), fontsize=12,
                                    color="blue")

    def draw_GRR_picture(self, GRR_picture_label_list, GRR_picture_y_value_list):
        # -------------------------- 画GRR图 -----------------
        if self.GRR_Image_mode:
            self.ax1_point.boxplot(GRR_picture_y_value_list, labels=GRR_picture_label_list, showmeans=True, sym='-')
            self.ax1_point.set_xlim(left=0, right=len(GRR_picture_label_list)+1)


    def change_current_item_name(self, each_item):
        if len(self.current_item) == 1:
            return ""
        else:
            if len(each_item) > 14:
                return each_item[:7] + "..." + each_item[-7:]
            else:
                return each_item

    def draw_main_picture(self, item_data, all_y_value_list, final_upper_limit, final_lower_limit):
        ax2_xmax, ax2_xmin = self.get_list_max_min(all_y_value_list + [[final_upper_limit, final_lower_limit]])
        GRR_picture_label_list, GRR_picture_y_value_list = [], []
        for each_item in item_data:
            unit, upper_limit, lower_limit, time_value_list, y_value_list = \
                item_data[each_item][0], item_data[each_item][1], item_data[each_item][2], item_data[each_item][3], \
                item_data[each_item][4]
            # 画散点图和直方图
            for i in range(len(y_value_list)):
                # --------- 是否用图例 -----------------
                current_xx = self.current_select_xx[each_item][i]
                time_value = time_value_list[i]
                #  获取x,y轴的值
                x_value, y_value = self.get_point_value(y_value_list[i], time_value)
                item_name = self.change_current_item_name(each_item)
                self.draw_point_hist_picture(i, each_item, item_name, y_value_list, x_value, y_value, ax2_xmax,
                                             ax2_xmin, current_xx)
                GRR_picture_label_list.append(item_name + " " + current_xx)
                GRR_picture_y_value_list.append(y_value)
            self.draw_lengend(y_value_list)
            self.draw_normal_school(all_y_value_list, final_lower_limit, final_upper_limit)

        self.draw_limit(final_lower_limit, final_upper_limit, ax2_xmax)
        self.draw_GRR_picture(GRR_picture_label_list, GRR_picture_y_value_list)
        self.ax1_point.locator_params(axis='y', nbins=20)  # 纵刻度数为20
        self.ax2_point.locator_params(axis='x', nbins=20)  # 横轴刻度数为20
        self.ax2_point.locator_params(axis='y', nbins=20)  # 纵刻度数为20
        self.ax1_point.tick_params(axis="x", labelrotation=45)  # 轴标签角度30
        self.ax2_point.tick_params(axis="x", labelrotation=45)  # 轴标签角度30
        # figure.autofmt_xdate(rotation=40)  # 绘制斜的日期标签，以免它们彼此重叠

        # 设定x坐标从0开始
        if not self.x_axis_is_time_mode and not self.GRR_Image_mode:
            self.ax1_point.set_xlim(left=0)
        # 自定义y最小值
        if self.minimum_entry_value != "":
            if self.is_float(self.minimum_entry_value):
                self.ax1_point.set_ylim(bottom=float(self.minimum_entry_value))
                self.ax2_point.set_xlim(left=float(self.minimum_entry_value))

    def reflesh_Draw_picture_GUI(self,Draw_picture_GUI):
        self.Draw_picture_GUI = Draw_picture_GUI
        self.insight_csv_data = self.Draw_picture_GUI.insight_csv_data
        self.current_item = self.Draw_picture_GUI.current_item
        self.current_item_name = self.Draw_picture_GUI.current_item_name
        self.current_color_by = self.Draw_picture_GUI.color_by_string_var.get()
        self.current_select_xx = self.Draw_picture_GUI.current_select_xx
        self.color_dict = self.Draw_picture_GUI.color_dict

        self.user_define_lower_limit = self.Draw_picture_GUI.lower_limit_entry.get()
        self.user_define_upper_limit = self.Draw_picture_GUI.upper_limit_entry.get()
        self.x_axis_is_time_mode = self.Draw_picture_GUI.draw_picture_mode["X axis is time"].get()
        self.remove_invalid_mode = self.Draw_picture_GUI.draw_picture_mode["remove_invalid"].get()
        self.GRR_Image_mode = self.Draw_picture_GUI.draw_picture_mode["Box image"].get()
        self.bar_no_filled_mode = self.Draw_picture_GUI.draw_picture_mode["bar no filled"].get()
        self.is_normed_mode = self.Draw_picture_GUI.draw_picture_mode["Is normed"].get()
        self.remove_limit_mode = self.Draw_picture_GUI.draw_picture_mode["Remove limit"].get()
        self.vertical_line = self.Draw_picture_GUI.vertical_line_entry.get()
        self.minimum_entry_value = self.Draw_picture_GUI.minimum_entry.get()

    def show_main_picture(self, Draw_picture_GUI):
        self.reflesh_Draw_picture_GUI(Draw_picture_GUI)
        item_data = {}  # 待显示的数据
        all_y_value_list = []
        final_upper_limit, final_lower_limit = "", ""
        for each_item in self.current_item:
            if each_item in self.current_select_xx:
                time_value_list, y_value_list = self.get_x_y_value_list(
                    each_item)  # y_value_list 是二维列表 [[...],[...],...]
                unit, upper_limit, lower_limit = self.get_limit(each_item)
                all_y_value_list += y_value_list  # all_y_value_list 也是二维列表
                if self.current_item.index(each_item) == 0:
                    final_upper_limit, final_lower_limit = upper_limit, lower_limit
                else:
                    if self.is_a_larger_b(upper_limit, final_upper_limit):
                        final_upper_limit = upper_limit
                    if self.is_a_larger_b(final_lower_limit, lower_limit):
                        final_lower_limit = lower_limit
                item_data[each_item] = [unit, upper_limit, lower_limit, time_value_list, y_value_list]
        self.init_distinguish_picture(item_data, all_y_value_list, final_upper_limit, final_lower_limit)
        self.draw_main_picture(item_data, all_y_value_list, final_upper_limit, final_lower_limit)
        self.Draw_picture_GUI.frame_canvas.update()
        print("画布大小", self.Draw_picture_GUI.frame_canvas.winfo_width())


def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while "\\" in path:
        path = path.replace("\\", "")
    return path

def main(csv_file_path_list):
    insight_csv_data = Insight_csv_data(csv_file_path_list)
    insight_csv_data.start_load_picture_data()
    draw_picture_GUI = Draw_picture_GUI(csv_file_path_list, insight_csv_data)

def run_draw_picture(csv_file_path_list):
    run_draw_picture_process = Process(target=main, args=(csv_file_path_list,))
    run_draw_picture_process.daemon = True
    run_draw_picture_process.start()

if __name__ == "__main__":
    csv_file_path_list = eval(sys.argv[1])
    main(csv_file_path_list)
