#! /usr/bin/env python3
# ! /usr/bin/env python
import platform
import traceback
# import re
import os
# import sys
# import time
# from datetime import datetime
# from time import sleep
# import math
# import random
# from time import sleep
# import threading
# from multiprocessing import Process
# from multiprocessing import Queue
# from multiprocessing import Pool
# from multiprocessing import Manager
import tkinter as tk
# from tkinter import ttk
# import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
# 第三方库
# import csv
# import xlwt
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.backend_bases import key_press_handler
# from matplotlib.figure import Figure
import matplotlib.dates as mdate
import matplotlib.mlab as mlab
import numpy as np
from scipy.stats import norm
import pandas as pd

# 我的库
# from haimeng_xlwt import Haimeng_xlwt
from draw_picture_GUI import DrawPictureGUI
if platform.system() == "Windows":
    import ctypes


def is_float(string):
    i = 0
    for each_s in str(string):
        i += 1
        if not each_s.isdigit() and each_s != ".":
            if i == 1:
                if each_s == "-":
                    continue
            else:
                return False
        else:
            return True


class InsightCsvData:
    def __init__(self, csvpath):
        """
        解析insight_csv数据
        """
        self.my_path = csvpath
        self.measure_data_start_line_index = 5
        self.FOM_start_column_index = 11  # 6
        self.start_time_column_index = 8  # 6
        # 标题行为第一行，标题列为时间列，将时间转化格式
        self.data_fm = pd.read_csv(self.my_path, header=1, index_col=self.start_time_column_index,
                                   parse_dates=[self.start_time_column_index], dayfirst=True)
        self.head_line = self.data_fm.columns
        self.test_FOMs = self.head_line[self.FOM_start_column_index:]  # 可迭代对象
        self.all_data_list = ["all_data"]
        # 移除重复项 和 值为空的行
        self.SN_list = self.data_fm["SerialNumber"][self.measure_data_start_line_index:].drop_duplicates().dropna()
        self.station_list = self.data_fm["Station ID"][self.measure_data_start_line_index:].drop_duplicates().dropna()
        self.special_build_list = self.data_fm["Special Build Description"][
                                  self.measure_data_start_line_index:].drop_duplicates().dropna()
        self.option_dict = {
            "all_data": self.all_data_list,
            "SerialNumber": self.SN_list,
            "Station ID": self.station_list,
            "Special Build Description": self.special_build_list
        }
        # 其他获取数据方法
        # SN_list_data = self.data_fm[self.data_fm["SerialNumber"] == "GY6DX00N0FKV"].loc[:,"AC_CP"]
        # self.get_option_dada("SerialNumber",["AC_CP","crown_force"],["GY6DX00N0FKV","GY6DX00Y4FKV"])
        # self.get_option_dada("SerialNumber", "AC_CP", )
        # data = self.get_option_dada_group("SerialNumber",["AC_CP", "crown_force"],["GY6DX00N0FKV","GY6DX00Y4FKV"] )
        # limit = self.get_limit("AC_CP")

    # 获取二维数据
    def get_option_dada_group(self, option, item_list):
        """
        如果option是全部数据，则返回测试项所在列的全部值， 根据 返回结果[测项名称]  获取其中一个侧项的值
        如果option是按 SN/Statio...分类的数据， 则返回对应的pd分组，根据  返回结果.get_group(SN名)[测试项名].astype(float)获取某个测项某个SN的值
        """
        if option != "all_data":
            return self.data_fm.loc[:, [option]+item_list].groupby(option)
        else:
            return self.data_fm.loc[:, item_list][self.measure_data_start_line_index:].astype(float)

    def get_limit(self, item):
        """
        upper {limit[0]}, lower {limit[1]} unit{limit[2]
        """
        limit = self.data_fm[item][2:5]
        return limit

    @staticmethod
    def get_cpk(upper_limit, lower_limit, std_value, mean_value):
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
        return cpu, cpl, cpk

    # def get_fail_num(self, item_name, lower, upper):
    #     result = self.data_fm[item_name].astype(float)

    # def get_option_dada(self, option, item_list, xx_list):
    #     if option != "all_data":
    #         data = self.data_fm[self.data_fm[option].isin(xx_list)].loc[:, item_list].astype(float)
    #         # max_value = data.max()
    #         # min_value = data.min()
    #         # print("最大", max_value)
    #         # print("最小", min_value)
    #     else:  # 全部数据
    #         data = self.data_fm.loc[:, item_list][self.measure_data_start_line_index:].astype(float)
    #     return data
    #
    # 获取一维数据
    # def get_xx_data(self,option, item_name, xx_name):
    #     if option != "all_data":
    #         result = self.data_fm[self.data_fm[option] == xx_name][item_name].astype(float)
    #     else:
    #         result = self.data_fm[item_name][self.measure_data_start_line_index:].astype(float)
    #     return result


class DrawPictureAppInit(DrawPictureGUI):
    def __init__(self, csvpath):
        """
        1. 创建GUI
        2. 获取数据
        3. 显示文件名和测试项
        4. 显示数据分类
        5. 绑定事件
        6. 创建画图对象，显示初始化图片
        """
        super().__init__()
        self.show_test_item_max = 5
        self.csv_path = csvpath
        self.insight_csv_data = InsightCsvData(csvpath)
        self.current_select_item = [self.insight_csv_data.test_FOMs[0]]
        self.item_name_frame_obj.show_item_name(self.csv_path, self.insight_csv_data.test_FOMs)
        self.color_by_obj.reflesh_option_list(self.current_select_item, self.insight_csv_data.option_dict)
        self.update_panda_data()
        self.bind_event()
        self.draw_piture_obj = DrawPixture(screen_width=self.screenwidth, screen_height=self.screenheight)
        self.figure_canvas = FigureCanvasTkAgg(self.draw_piture_obj.figure, master=self.frame_canvas)
        self.figure_canvas.get_tk_widget().grid(row=0, column=0, sticky="wnse")
        self.draw_picture()
        self.root.mainloop()

    def change_picture_event(self, fun, *args):
        fun(*args)
        self.draw_picture()

    def bind_event(self):
        """
        1. 点击测试项
        2. 点击listbox
        3. 改变筛选菜单
        """
        self.item_name_frame_obj.item_name_list_box.bind("<ButtonRelease-1>", self.click_item_name)
        self.item_name_frame_obj.item_name_list_box.bind("<KeyRelease-Up>", self.click_item_name)
        self.item_name_frame_obj.item_name_list_box.bind("<KeyRelease-Down>", self.click_item_name)
        self.color_by_obj.xx_list_box.bind("<ButtonRelease-1>", self.click_list_box)
        self.color_by_obj.xx_list_box.bind("<KeyRelease-Up>", self.click_list_box)
        self.color_by_obj.xx_list_box.bind("<KeyRelease-Down>", self.click_item_name)
        self.color_by_obj.color_by_string_var.trace_variable("w", self.color_by_string_var_event)
        self.title_entry_frame_obj.upper_limit_entry.bind("<KeyRelease-Return>", self.draw_picture)
        self.title_entry_frame_obj.lower_limit_entry.bind("<KeyRelease-Return>", self.draw_picture)
        self.title_entry_frame_obj.vertical_line_entry.bind("<KeyRelease-Return>", self.draw_picture)
        self.title_entry_frame_obj.minimum_entry.bind("<KeyRelease-Return>", self.draw_picture)

        change_legend_FUN = lambda : self.change_picture_event(self.draw_piture_obj.change_legend_location)
        self.title_button_frame_obj.button_name_dict["Legend position"]["command"] = change_legend_FUN
        larger_dot_FUN = lambda: self.change_picture_event(self.draw_piture_obj.zoom_out_point)
        self.title_button_frame_obj.button_name_dict["Larger dot"]["command"] = larger_dot_FUN
        smaller_dot_FUN = lambda: self.change_picture_event(self.draw_piture_obj.zoom_in_point)
        self.title_button_frame_obj.button_name_dict["Smaller dot"]["command"] = smaller_dot_FUN
        change_color_FUN = lambda: self.change_picture_event(self.color_by_obj.reflesh_option_list,
            self.current_select_item, self.insight_csv_data.option_dict)
        self.title_button_frame_obj.button_name_dict["Change color"]["command"] = change_color_FUN
        self.title_button_frame_obj.button_name_dict["Save this image"]["command"] = self.save_this_image

    def update_panda_data(self):
        """
        获取当前选项的全部数据
        1. all_data: self.panda_data={item_name: data}
        2. self.panda_data.get_group(xx_name)[item_name].astype(float)
        """
        self.panda_data = self.insight_csv_data.get_option_dada_group(self.color_by_obj.color_by_string_var.get(),
                                                                     self.current_select_item)

    def click_item_name(self, event=None):
        """
        点击测试项事件，如果选项改变：
            如果选项大于1个或者由多个变少，则重新生成筛选项和颜色空间
            更新当前选项，获取当前选项数据，画图
        """
        current_select_item = self.item_name_frame_obj.click_item_name(self.insight_csv_data.test_FOMs,
                                                                       self.current_select_item)
        if len(current_select_item)>self.show_test_item_max:
            tkmessage.showwarning("Hi", "最多只能选择五个测项！")
            return
        if current_select_item != self.current_select_item:
            if len(current_select_item)>1 or len(self.current_select_item)>1:
                self.color_by_obj.reflesh_option_list(current_select_item, self.insight_csv_data.option_dict)
            self.current_select_item = current_select_item
            self.update_panda_data()
        self.draw_picture()

    def click_list_box(self, event=None):
        """
        点击筛选列表框： 获取当前选项，画图
        """
        self.color_by_obj.click_list_box(event)
        self.draw_picture()

    def color_by_string_var_event(self, x, y, z):
        """
        改变筛选菜单， 重新生成筛选项，更新数据，画图
        """
        self.color_by_obj.color_by_string_var_event(self.current_select_item, x, y, x)
        self.update_panda_data()
        self.draw_picture()

    def draw_picture(self, event=None):
        pass


class DrawPictureApp(DrawPictureAppInit):
    def __init__(self, csv_path):
        super().__init__(csv_path)
        self.limit_color = ["red", "yellow", "blue", "green", "black"]
        self.current_item_name = ""

    def get_y_value(self, item_name, xx_name):
        """
        获取某个选项的数据
        """
        if self.color_by_obj.color_by_string_var.get() == "all_data":
            y = self.panda_data[item_name]
        else:
            y = self.panda_data.get_group(xx_name)[item_name].astype(float)
        return y

    @classmethod
    def get_max_min(cls, max, min, max_old, min_old):
        if is_float(max) and is_float(max_old):
            if float(max)<float(max_old):
                max = max_old
        else:
            max = max_old
        if is_float(min) and is_float(min):
            if float(min)>float(min_old):
                min = min_old
        else:
            min = min_old
        return float(max), float(min)

    def get_title_name(self, item_name, old_name):
        if not old_name:
            return item_name
        elif item_name not in old_name:
            if len(old_name + "&" + item_name)<50:
                return old_name + "&" + item_name
            else:
                return old_name + "..."

    def get_limit(self, item_name, old_upper, old_lower, **kwargs):
        [upper, lower, unit] = self.insight_csv_data.get_limit(item_name)
        if old_upper is not None:
            upper, lower = \
                DrawPictureApp.get_max_min(upper, lower, old_upper, old_lower)
            unit = "NA"
        if is_float(kwargs["upper"]):
            upper = kwargs["upper"]
        if is_float(kwargs["lower"]):
            lower = kwargs["lower"]
        if kwargs["remove_limit"]:
            upper, lower = "nan", "nan"
        return upper, lower, unit

    def get_title_value(self, **kwargs):
        """
        result_dict = {
                          "upper": xxx, "lower": xxx, "unit": xxx,
                          "y_list": [[...],[...],[...]],  # 保存的是panda frame类型
                          "y_dict": {each_xx1:[...], each_xx2:[...]},
                          "item_name": "xxx",
                          "max/min/mean/count/std": xxx,
                          "cpy/cpk/cpl": xxx
                      }
        """
        result_dict = {}
        result_dict["y_dict"] = {}
        result_dict["y_list"] = []
        result_dict["item_name"] = ""
        result_dict["upper"], result_dict["lower"]= None, None
        for each_xx in self.color_by_obj.current_select:
            search_result = self.color_by_obj.get_item_xx_name(each_xx, self.current_select_item)
            if search_result is not None:
                [item_name, xx_name] = search_result
                result_dict["item_name"] = self.get_title_name(item_name, result_dict["item_name"])
                result_dict["upper"], result_dict["lower"], result_dict["unit"]  = self.get_limit(
                                                item_name, result_dict["upper"], result_dict["lower"], **kwargs)
                print("limit:",result_dict["upper"], result_dict["lower"])
                y = self.get_y_value(item_name, xx_name)
                result_dict["y_dict"][each_xx] = y
                result_dict["y_list"].append(y)
        merge_y = pd.concat(result_dict["y_list"])  # 合并多维数据为一维数据?
        max_, min_, mean_, count_, std_ = merge_y.agg(['max', 'min', 'mean', 'count', 'std'])  # "median"
        result_dict["max"], result_dict["min"], result_dict["mean"], \
            result_dict["count"], result_dict["std"] = max_, min_, mean_, count_, std_
        result_dict["fail"] = len(merge_y[(merge_y > float(result_dict["upper"])) |
                                                     (merge_y < float(result_dict["lower"]))])
        del result_dict["y_list"]
        result_dict["cpu"], result_dict["cpl"], result_dict["cpk"] = \
            self.insight_csv_data.get_cpk(result_dict["upper"], result_dict["lower"],
                result_dict["mean"], result_dict["std"])
        return result_dict

    def init_title(self, result_dict):
        """
        ax1_x: 测试项总的测试次数，fail的个数
        ax1_y: 测试项测试 单位，limit
        ax2_x: 测试项单位，limit，最大，最小，平均，std，cpu，cpl，cpk
        ax2_y: 测试次数
        标题： 测试项名称
        """
        ax1_x = f"Total: {result_dict['count']}, Fail: {result_dict['fail']}"
        ax1_y = (f"Unit: {result_dict['unit']}, Upper: {result_dict['upper']}, "
                 f"Lower:{result_dict['lower']}")
        ax1_title = result_dict["item_name"]
        ax2_x = ax1_y + (f", Max:{result_dict['max']}, Min:{result_dict['min']}\n "
                         f"Mean:{result_dict['mean']}, Std:{result_dict['std']:.3%}, "
                         f"Cpu:{result_dict['cpu']}, Cpl:{result_dict['cpl']}, "
                         f"Cpk:{result_dict['cpk']}")
        ax2_y = "Count"
        ax2_title = result_dict["item_name"]
        self.current_item_name = result_dict["item_name"]
        return [ax1_x, ax1_y, ax1_title, ax2_x, ax2_y, ax2_title]

    def init_mode(self):
        mode_dict = {}
        mode_dict["Minimum"] = self.title_entry_frame_obj.minimum_entry.get()
        mode_dict["Vertical_line"] = self.title_entry_frame_obj.vertical_line_entry.get()
        mode_dict["upper"] = self.title_entry_frame_obj.upper_limit_entry.get()
        mode_dict["lower"] = self.title_entry_frame_obj.lower_limit_entry.get()
        mode_dict["x_is_time"] = self.title_entry_frame_obj.draw_picture_mode["X axis is time"].get()
        mode_dict["remove_limit"] = self.title_entry_frame_obj.draw_picture_mode["Remove limit"].get()
        mode_dict["fill_bar"] = self.title_entry_frame_obj.draw_picture_mode["Fill bar"].get()
        mode_dict["is_normed"] = self.title_entry_frame_obj.draw_picture_mode["Is normed"].get()
        print("是否显示时间", mode_dict)
        return mode_dict

    def draw_picture_(self, result_dict, mode_dict):
        y_max, y_min = DrawPictureApp.get_max_min(result_dict["upper"], result_dict["lower"],
                                                  float(result_dict["max"]), float(result_dict["min"]))
        i = 0
        y_value_list = []
        for each_xx in self.color_by_obj.current_select:
            if each_xx in result_dict["y_dict"]:
                y = result_dict["y_dict"][each_xx]
                y_value_list += list(y)
                if not mode_dict["x_is_time"]:
                    x = np.arange(len(y))
                else:
                    x = y.index
                color = self.color_by_obj.color_dict[each_xx]
                scatter_label = each_xx
                self.draw_piture_obj.draw_hist_picture(x, y, y_max, y_min, color, scatter_label, **mode_dict)
                i += 1
        self.draw_piture_obj.draw_limit(result_dict["upper"], result_dict["lower"], y_max, **mode_dict)
        self.draw_piture_obj.draw_normal_school(y_value_list, result_dict["min"], result_dict["max"],
                                                result_dict["mean"], result_dict["std"], **mode_dict)
        self.draw_piture_obj.draw_lengend(int(i/10)+1)
        angle = 0
        if len(y_value_list)>1000 or y_min<1 or y_max>1000 or mode_dict["x_is_time"]:
            angle=45
        self.draw_piture_obj.set_picture(angle, **mode_dict)

    def draw_picture(self, event=None):
        try:
            mode_dict = self.init_mode()
            result_dict = self.get_title_value(**mode_dict)
            self.draw_piture_obj.init_picture(*self.init_title(result_dict))
            self.draw_picture_(result_dict, mode_dict)
            self.figure_canvas.draw()
        except Exception as e:
            print("画图出错啦", str(e))
            traceback.print_exc()

    def save_this_image(self, is_show_message=True):
        folder_name = self.color_by_obj.color_by_string_var.get()
        dir_path = os.path.dirname(self.csv_path) + "/" + folder_name
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        save_path = dir_path + '/' + self.current_item_name + '.png'
        self.draw_piture_obj.figure.savefig(save_path, bbox_inches='tight')  # 保存图片
        if is_show_message:
            tk.messagebox.showinfo("Hi", "Result have been save at %s"%(save_path))


class DrawPixture:
    def __init__(self, **kwargs):
        # figsize = kwargs["figsize"] if "figsize" in kwargs else (14.5, 4.15)
        if "screen_width" in kwargs:
            print(kwargs["screen_width"], kwargs["screen_height"])
            if platform.system()=="Windows":
                scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
                figsize = (1*kwargs["screen_width"]/scale_factor, 0.65*kwargs["screen_height"]/scale_factor)
            else:
                figsize = (kwargs["screen_width"]/100, 0.5*kwargs["screen_height"]/100)
        self.figure, axs = plt.subplots(nrows=1, ncols=2, dpi=100, figsize=figsize,
                                        facecolor="LightGrey")
        self.ax1_point = axs[0]
        self.ax2_point = axs[1]
        self.point_size = 3
        self.line_size = 1.2
        self.legend_location_list = ["upper right", "lower right", "lower left", "upper left", "best", None]
        self.legend_location = self.legend_location_list[0]

    def init_picture(self, *args):
        self.ax1_point.cla()
        self.ax2_point.cla()
        self.ax1_point.set_position([0.06, 0.195, 0.44, 0.725])  # 坐标轴距离左边0.05，距离底部0.2，宽度0.45，高度0.75
        self.ax2_point.set_position([0.56, 0.195, 0.42, 0.725])
        self.ax1_point.grid(color="gray", which='major', axis='both', ls="dashed", lw=0.5, alpha=0.5)
        self.ax2_point.grid(color="gray", which='major', axis='both', ls="dashed", lw=0.5, alpha=0.5)
        # -----------  ax1 标题 设置 ------------
        self.ax1_point.set_xlabel(args[0], fontsize=10, color="black")
        self.ax1_point.set_ylabel(args[1], fontsize=10, color="black")  # 纵坐标名字设置
        self.ax1_point.set_title(args[2], fontsize=11, color="Blue")  # 设置标题名字
        # -----------  ax2 标题 设置 ------------
        self.ax2_point.set_xlabel(args[3], fontsize=10, color="black")
        self.ax2_point.set_ylabel(args[4], fontsize=10, color="black")
        self.ax2_point.set_title(args[5], fontsize=11, color="Blue")  # 设置标题名字

    def draw_hist_picture(self, x, y, y_max, y_min, color, scatter_label, **kwargs):
        self.ax1_point.plot(x, y, c=color, marker="o",
                            markersize=self.point_size, linestyle="--", linewidth=0.3, label=scatter_label)
        hist_type = "step"
        if kwargs["fill_bar"]:
            hist_type = "bar"
        tops, bins, patch_list = self.ax2_point.hist(y, bins=50,
                                                     range=(y_min, y_max),
                                                     color=color,
                                                     density=kwargs["is_normed"],
                                                     histtype=hist_type,
                                                     linewidth=self.line_size,
                                                     stacked=True,
                                                     label=scatter_label)

    def draw_limit(self, upper_limit, lower_limit, vertical_location, **kwargs):
        if is_float(str(upper_limit)):
            print("绘制上限", upper_limit)
            self.ax1_point.axhline(float(upper_limit), linewidth=1.5, linestyle='--', color="red")  # 画下限
            self.ax2_point.axvline(float(upper_limit), linewidth=1.5, linestyle='--', color="red")
        if is_float(str(lower_limit)):
            self.ax1_point.axhline(float(lower_limit), linewidth=1.5, linestyle='--', color="red")  # 画上限
            self.ax2_point.axvline(float(lower_limit), linewidth=1.5, linestyle='--', color="red")
        if is_float(kwargs["Vertical_line"]):
            self.ax1_point.axvline(float(kwargs["Vertical_line"]), linewidth=1, linestyle='--', color="blue")  # 画竖线

            self.ax1_point.text(x=float(kwargs["Vertical_line"]), y=vertical_location*0.8,
                                s=r"$%s$" % (kwargs["Vertical_line"]), fontsize=12, color="blue")

    def draw_normal_school(self, y_value_list, min, max, mean, std, **kwargs):
        # -------------------------- 画正态分布图 -----------------
        if kwargs["is_normed"]:
            x_value = np.linspace(float(min), float(max), 1000)
            kde = mlab.GaussianKDE(y_value_list)  # 核密度曲线
            self.ax2_point.plot(x_value, kde(x_value), color="red", linewidth=1.5, linestyle="--")
            y_value = norm.pdf(x_value, float(mean), float(std))  # 正态分布曲线
            self.ax2_point.plot(x_value, y_value, color="green", linewidth=1.5, linestyle="--")

    def draw_lengend(self, legend_column):
        # ----------------- 画图例 --------------------------
        self.ax1_point.legend(loc=self.legend_location, fontsize=6, ncol=legend_column)
        self.ax2_point.legend(loc=self.legend_location, fontsize=6, ncol=legend_column)

    def set_picture(self, xangle, **kwargs):
        self.ax1_point.locator_params(axis='x', nbins=20)  # 刻度数为20
        self.ax1_point.locator_params(axis='y', nbins=20)  # 刻度数为20
        self.ax1_point.tick_params(axis="x", labelrotation=xangle)  # 轴标签角度30

        self.ax2_point.locator_params(axis='x', nbins=20)  # 横轴刻度数为20
        self.ax2_point.locator_params(axis='y', nbins=20)  # 纵刻度数为20
        self.ax2_point.tick_params(axis="x", labelrotation=xangle)  # 轴标签角度30

        # 设定x坐标从0开始
        if not kwargs["x_is_time"]:  # and not self.GRR_Image_mode:
            self.ax1_point.set_xlim(left=0)
        # 自定义y最小值
        if kwargs["Minimum"] and is_float(kwargs["Minimum"]):
                self.ax1_point.set_ylim(bottom=float(kwargs["Minimum"]))
                self.ax2_point.set_xlim(left=float(kwargs["Minimum"]))

    def change_legend_location(self):
        current_index = self.legend_location_list.index(self.legend_location)
        if current_index == len(self.legend_location_list) - 1:
            current_index = 0
        else:
            current_index += 1
        self.legend_location = self.legend_location_list[current_index]

    def zoom_in_point(self):
        if self.point_size > 1 and self.line_size > 1:
            self.point_size -= 1
            self.line_size -= 1

    def zoom_out_point(self):
        if self.point_size < 20 and self.line_size < 10:
            self.point_size += 1
            self.line_size += 1


if __name__ == "__main__":
    csv_path = "/Users/15400155/Desktop/HS_4.0.1/data/insight-data.csv"
    # csv_path = "/Users/15400155/Desktop/HS_4.0.1/data/insight_data_biggist_size.csv"
    draw_picture_app = DrawPictureApp(csv_path)