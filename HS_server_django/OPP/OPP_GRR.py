import pandas
import numpy as np
import matplotlib
matplotlib.use('Agg')#设置成无gui模式
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv
import copy
from io import BytesIO
import random

class GUI:
    def __init__(self):
        """
        输出筛选的测试项，分类
        """
        group_key = [{"SerialNumber": []}, {"Station ID": []}, {"Version": []}]


class CSV2pd:
    '''
    根据分类生成数据
    1. 非有效数据行的处理
    2.
    '''

    def __init__(self, path):
        # self.path = copy.deepcopy(path)
        self.path = path
        self.df = pandas.read_csv(self.path, header=0, low_memory=False)
        self.UPPER_LIMIT_LINE_INDEX = 2
        self.LOWER_LIMIT_LINE_INDEX = 3
        self.UNIT_LINE_INDEX = 4
        self.MEASUREMENT_DATA_START_LIN_INDEXE = 5
        self.is_insight_csv = True if "Parametric" in self.df.columns else False

        if self.is_insight_csv:
            self.ITEM_LIST_START_COLUMN_INDEX = list(self.df.columns).index("Parametric")
            self.df = pandas.read_csv(self.path, header=1)
        else:
            # display_name_line, PDCA_Priority, Upper_Limit, Lower_Limit, Measurement Unit= [],[],[],[],[]
            self.ITEM_LIST_START_COLUMN_INDEX = 0
            df2_data = []
            for i in range(0, 5):
                df2_data.append(["" for j in self.df.columns])
            df2 = pandas.DataFrame(df2_data, columns=self.df.columns)
            self.df = pd.concat([df2, self.df], ignore_index=True)
            

    def group_data(self, key_list):
        '''
        根据筛选项返回对应的y轴值
        group_by 方法：根据给定的多个键进行分组，返回分组后的二元祖，元祖中第一个元素是分组后的键，第二个元素是分组后的值
        for i in result:
            print(i[0], i[1]["AC_CP"])
        get_group方法：根据分组后的键，获取对应的值
        print(result.get_group(("C4N6RR76CJ", "ITJS_A02-3FAS-01_6_TEST5", "version1"))["AC_CP"])
        '''
        self.df_copy = self.df.drop([0,1,2,3,4])
        # todo 重定义索引值
        return self.df_copy.groupby(key_list)

    def group_key(self, group_data):
        result = []
        for i in group_data:
            if isinstance(i[0], tuple):
                result.append(i[0])
            else:  # 当只有一种分类时，分组的键值不再是元祖，而是字符串
                result.append((i[0],))
        return result

    @property
    def item_list(self):
        return list(self.df.columns[self.ITEM_LIST_START_COLUMN_INDEX:])

    @property
    def factor_list(self):
        if self.is_insight_csv:
            return list(self.df.columns[:self.ITEM_LIST_START_COLUMN_INDEX])
        else:
            return list(self.df.columns)

    def item_info(self, item_name):
        item_info = {"name": item_name, "upper_limit": '', "lower_limit": '', "unit": "NA"}
        upper_limit = self.df[item_name][self.UPPER_LIMIT_LINE_INDEX]
        lower_limit = self.df[item_name][self.LOWER_LIMIT_LINE_INDEX]
        unit = self.df[item_name][self.UNIT_LINE_INDEX]
        item_info["upper_limit"], item_info["lower_limit"], item_info["unit"] = upper_limit, lower_limit, unit
        return item_info




class Picture:
    def __init__(self, item_info, key, data, picture_info):
        self.item_info, self.key, self.data, self.picture_info = item_info, key, data, picture_info

        self.max_col = 40
        self.ncol = len(key) if len(key) < self.max_col else self.max_col
        self.nrow = len(key) / self.ncol
        self.nrow = int(self.nrow) + 1 if self.nrow > int(self.nrow) else int(self.nrow)
        # print(self.ncol, self.nrow)
        self.subplot_height_inch = 4  # 一个子图高度
        self.top_title_height = 1
        self.bottom_title_height = 1
        hspace = 2
        figheight = self.subplot_height_inch * self.nrow + self.top_title_height + self.bottom_title_height + hspace * (
                    self.nrow - 1)
        self.figsize = (14, figheight)
        self.dpi = 100
        self.sub_left, self.sub_right, self.sub_bottom, self.sub_top = 5 / 100, 95 / 100, self.bottom_title_height / figheight, 1 - self.top_title_height / figheight
        self.sub_wspace, self.sub_hspace = 0, hspace / self.subplot_height_inch
        self.figure, self.axs = plt.subplots(nrows=self.nrow, ncols=self.ncol, dpi=self.dpi,
                                             figsize=self.figsize)  # ,edgecolor="red", facecolor="LightGray"
        self.figure.subplots_adjust(left=self.sub_left, right=self.sub_right, bottom=self.sub_bottom,
                                    top=self.sub_top, wspace=self.sub_wspace, hspace=self.sub_hspace)
        self.render = self.figure.canvas.get_renderer()
        self.subplot_height = self.subplot_height_inch * self.dpi
        self.subplot_width = self.figsize[0] * self.dpi * (self.sub_right - self.sub_left) / self.ncol
        self.figure.suptitle(item_info["name"], fontsize=16)

    def adjust_picture(self, top_hrate, bottom_hrate):
        '''
        top_title_height是顶部标题相对于子图高度的比例
        bottom_title_height是底部标题相对于子图高度的比例
        '''
        self.sub_hspace = top_hrate + bottom_hrate
        hspace = (top_hrate + bottom_hrate + 0.1) * self.subplot_height_inch  # 多增加0.1的空白间隔
        top_title_height = top_hrate * self.subplot_height_inch + self.top_title_height
        bottom_title_height = bottom_hrate * self.subplot_height_inch + self.bottom_title_height

        figheight = self.subplot_height_inch * self.nrow + top_title_height + bottom_title_height + hspace * (
                self.nrow - 1)
        self.sub_left, self.sub_right, self.sub_bottom, self.sub_top = 5 / 100, 95 / 100, bottom_title_height / figheight, 1 - top_title_height / figheight
        self.figure.set_size_inches(self.figsize[0], figheight)
        self.sub_wspace, self.sub_hspace = 0, hspace / self.subplot_height_inch
        self.figure.subplots_adjust(left=self.sub_left, right=self.sub_right, bottom=self.sub_bottom,
                                    top=self.sub_top, wspace=self.sub_wspace, hspace=self.sub_hspace)

    def get_ax(self, i, j):
        if self.nrow == 1 and self.ncol == 1:
            return self.axs
        elif self.nrow == 1:
            return self.axs[j]
        else:
            return self.axs[i][j]


class Multi_picture(Picture):
    def __init__(self, item_info, key, data, picture_info):
        '''
        根据数据生成图表:
        画图的参数全部可调，比如设置标题大小，角度可调, 函数里面的数字改为变量
        todo
        图片大小用变量来写
        根据行数来决定画布高度
        图片上下限调整
        '''
        super().__init__(item_info, key, data, picture_info)
        y = data[item_info['name']]
        max_l = []
        min_l = []
        for i in y:
            max_l.append(pd.Series(i[1], dtype="float64").max())
            min_l.append(pd.Series(i[1], dtype="float64").min())
        # self.ymax = max(pd.Series(y, dtype="float64"))
        # self.ymin = min(pd.Series(y, dtype="float64"))
        self.ymax = max(max_l)
        self.ymin = min(min_l)
        # 设置图的样式
        self.point_size = 2
        self.base_color = "blue"
        self.color_dict = self.generate_hightlight_color()
        # print("颜色是", self.color_dict)
        # 先绘散点图或设定上下限，否则标题位置会计算错误
        self.draw_picture()

    def draw_picture(self):
        self.draw_point()
        self.set_axis()
        self.set_title()

    def generate_hightlight_color(self):
        # factor = self.picture_info["hightlight_color"]
        color_dict = {}
        factor_l = []
        if "hightlight_color_index" in self.picture_info:
            k = self.picture_info["hightlight_color_index"]
            for each_key in self.key:
                if each_key[k] not in factor_l:
                    factor_l.append(each_key[k])
        # todo 生成不同的颜色值
        # color dict = {"SN1": color1, "SN2": color2}
        for i in factor_l:
            r, g, b = random.randint(0,240), random.randint(0,240), random.randint(0,240)
            color = (r/255, g/255, b/255)
            color_dict[i] = color
        return color_dict

    def get_hightlight_color(self, i, j):
        if self.color_dict:
            current_key = self.key[i*self.ncol+j]
            k = self.picture_info["hightlight_color_index"]
            color = self.color_dict[current_key[k]]
            return color
        else:
            return self.base_color

    def get_xy(self, key):
        if len(key) == 1:
            key = key[0]
        y = self.data.get_group(key)[self.item_info["name"]].astype(float).dropna()
        # y = pd.Series(y, dtype="float64")  # 转换数据类型，只有数字类型才支持设置刻度
        x = np.arange(y.size)
        return [x, y]

    def is_float(self, string):
        try:
            result = float(string)
            return True
        except:
            return False

    def get_ylim(self, ax):
        ymin, ymax = self.ymin, self.ymax
        if self.is_float(self.item_info["upper_limit"]) and float(self.item_info["upper_limit"]) > self.ymax:
            ymax = float(self.item_info["upper_limit"])
        if self.is_float(self.item_info["lower_limit"]) and float(self.item_info["lower_limit"]) < self.ymin:
            ymin = float(self.item_info["lower_limit"])
        return [ymin - (ymax - ymin) * 0.1, ymax + (ymax - ymin) * 0.1]

    def get_xlim(self, ax):
        x0, xmax = ax.get_xlim()
        return [x0 - (xmax - x0) * 0.1, xmax + (xmax - x0) * 0.1]

    # **************************** 画散点图 ***************************************
    def draw_limit(self, ax):
        if self.is_float(self.item_info["lower_limit"]):
            ax.axhline(float(self.item_info["lower_limit"]), linewidth=1, linestyle='-', color="red")
        if self.is_float(self.item_info["upper_limit"]):
            ax.axhline(float(self.item_info["upper_limit"]), linewidth=1, linestyle='-', color="red")

    def draw_point(self):
        for i in range(self.nrow):
            for j in range(self.ncol):
                if i * (self.ncol) + j >= len(self.key):
                    break
                ax = self.get_ax(i, j)
                [x, y] = self.get_xy(self.key[i * self.ncol + j])
                ax.plot(x, y, marker="o", markersize=self.point_size, linestyle="", color="blue")

    # **************************** 坐标轴设置 *******************************************
    def set_axis(self):
        for i in range(self.nrow):
            for j in range(self.ncol):
                ax = self.get_ax(i, j)  # 单行和多行对子图的切片方式不一样
                ax.set_xticks([])  # 隐藏所有底部坐标轴
                if j > 0 and i * (self.ncol) + j < len(self.key):
                    # ax.spines['left'].set_linewidth(0)####设置左边坐标轴的粗细
                    ax.spines['left'].set_color((230 / 255, 230 / 255, 230 / 255))
                    ax.spines['right'].set_color('none')
                    ax.set_yticks([])
                if i * (self.ncol) + j >= len(self.key):
                    # 多出来的没有数据的子图隐藏坐标轴
                    # 只显示每行第一个子图的纵坐标轴
                    ax.set_yticks([])
                    ax.set_xticks([])
                    ax.spines['right'].set_color('none')
                    if i * (self.ncol) + j > len(self.key):
                        ax.spines['left'].set_color('none')
                    ax.spines['top'].set_color('none')
                    ax.spines['bottom'].set_color('none')
                ax.locator_params(axis='y', nbins=20)
                ax.set_xlim(left=self.get_xlim(ax)[0], right=self.get_xlim(ax)[1])
                # 子图数据不一样，matplotlib自动设定的坐标轴也不一样，这里手动设置ylim让所有子图纵坐标都一样
                ax.set_ylim(bottom=self.get_ylim(ax)[0], top=self.get_ylim(ax)[1])

    # **************************** 设置标题 ***************************************
    def get_set_ax2(self, ax):
        ax2 = ax.twiny()
        ax2.set_xticks([])
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        return ax2

    def change_coord(self, ax, x, y):
        # 改变比例坐标（图片最大宽高用1表示）为图表内的轴坐标系
        x0, xmax = ax.get_xlim()
        y0, ymax = ax.get_ylim()
        width = xmax - x0
        height = ymax - y0
        return x0 + width * x, y0 + height * y

    def is_ver_line(self, k, i, j):
        # 是否画不同分类变量之间的分隔线
        if j == 0:
            return True if k == 0 else False
        current_key = self.key[i * self.ncol + j]
        last_key = self.key[i * self.ncol + j - 1]
        for i in range(0, k):
            if current_key[i] != last_key[i]:  # 如果上层需要画线，则这一层不需要画
                return False
        if current_key[k] != last_key[k]:  # 如果上层没有画线，检查这一层需不需要画线
            return True
        return False

    def get_title_distance(self, k, i, j):
        '''
        获取x顶部不同标题之间距离多少个子图
        '''
        if len(self.key[0])>1 and k==len(self.key[0])-1 :
            return 1
        distance = 1
        end = i * self.ncol + self.ncol  # i=0, j=39
        if end >= len(self.key):
            end = len(self.key)
        for dis in range(i * self.ncol + j + 1, end):
            if self.key[dis][k] == self.key[i * self.ncol + j][k]:
                distance += 1
            else:
                break
        return distance

    def get_font_dpi_size(self, ax, string, font_size):
        t = ax.text(x=0, y=0, s=string, fontsize=font_size)
        bb = t.get_window_extent(renderer=self.render)
        bb = t.get_tightbbox(self.render)
        t.remove()
        rate = self.figsize[0] * self.dpi / self.figure.bbox.size[0]
        return [(bb.x1 - bb.x0) * rate, (bb.y1 - bb.y0) * rate]

    def get_font_size(self, k):
        # 最底部标题size为8，每上升一层size+2
        if k == len(self.key[0]) - 1:
            return 8
        return (len(self.key[0]) - k - 1) * 2 + 6

    def get_title_angle(self, title, font_size, k, i, j):
        '''
        计算当前标题能否横放
        '''
        distance = self.get_title_distance(k, i, j)  # 当前标题和下一个标题的距离
        ax = self.get_ax(i, j)
        font_dpi_size = self.get_font_dpi_size(ax, title, font_size)
        if font_dpi_size[0] < self.subplot_width * distance:
            return [0, distance, font_dpi_size]
        else:
            return [90, distance, font_dpi_size]

    def is90(self, k, i=0, j=0):
        factor = ''
        for n, key in enumerate(self.key):  # 计算角度以及最高的标题高度
            if key[k] != factor:
                i, j = int(n / self.ncol), n % self.ncol
                angle, distance, font_dpi_size = self.get_title_angle(key[k], self.get_font_size(k), k, i, j)
                if angle == 90:
                    return True
            factor = key[k]
        return False

    def get_xtitle_loc(self):
        '''
        获取表格每一层竖线的高度，字体摆放角度，字体大小，字体占据的ppi尺寸，字体摆放的位置
        '''
        result = [{'height': 1, 'angle': 0, 'font_size': 8, "font_xcoords": {}, 'font_height': 0} for i in self.key[0]]
        for k, d in enumerate(result):  # 遍历每一层标题
            is90 = self.is90(k)
            result[k]['angle'] = 90 if is90 else 0
            result[k]['font_size'] = self.get_font_size(k)
            factor = ''
            font_dpi_size_max = [0, 0]
            for n, key in enumerate(self.key):
                if key[k] != factor:
                    # 计算最高的标题高度
                    i, j = int(n / self.ncol), n % self.ncol
                    angle, distance, font_dpi_size = self.get_title_angle(key[k], result[k]['font_size'], k, i, j)
                    for x in range(0, 2):
                        if font_dpi_size[x] > font_dpi_size_max[x]:
                            font_dpi_size_max[x] = font_dpi_size[x]
                    #  计算标题居中位置
                    fontwidth = font_dpi_size[1] if is90 else font_dpi_size[0]
                    result[k]["font_xcoords"][f"{k}{i}{j}"] = (
                                                                          distance * self.subplot_width - fontwidth) / 2 / self.subplot_width
                    factor = key[k]
            result[k]['font_height'] = font_dpi_size_max[0] / self.subplot_height if is90 else font_dpi_size_max[
                                                                                                   1] / self.subplot_height
        return result

    def check_color(self, num):
        if num > 255:
            return 255
        if num < 0:
            return 0
        return num

    def cal_table_height(self, k, title_loc, show_list=None):
        show_list = self.key[0] if show_list is None else show_list
        height = 1
        for m in range(k, len(show_list)):
            height += title_loc[m]['font_height'] + 10 / self.subplot_height
        return height

    def set_xtop_title_table(self, ax, i, j, k, title_loc, show_list=None):
        '''
        设定表格标题背景色
        '''
        show_list = self.key[i * self.ncol + j] if show_list is None else show_list
        height = self.cal_table_height(k, title_loc, show_list)
        if (j == 0) or (self.key[i * self.ncol + j][k] != self.key[i * self.ncol + j - 1][k] and j > 0):
            # 填充色, fill_between函数的作用是在两条y曲线之间填充颜色，由于颜色可能会覆盖文字，因此颜色和文字只能由同一个子图来画，然后
            # 通过zorder来控制显示优先级
            base_color, step = 100, 20
            color = (
                self.check_color(base_color + k * step + 60) / 255, self.check_color(base_color + k * step + 100) / 255,
                (255) / 255)
            bottom = self.cal_table_height(k + 1, title_loc, show_list)
            top = height
            x = ax.get_xlim()
            dis = self.get_title_distance(k, i, j)
            ax.fill_between([x[0], x[1] + (dis - 1) * (x[1] - x[0])], self.change_coord(ax, 0, bottom)[1],
                            self.change_coord(ax, 0, top)[1], color=color, zorder=-1, clip_on=False)
            # 表格竖线，需要计算是否该画线和线的高度
            ymin = self.cal_table_height(k+1, title_loc, show_list)
            ax.axvline(ax.get_xlim()[0], ymin=ymin, ymax=top,
                       linewidth=1, linestyle='-', color="black", clip_on=False)
            if j!=0:
                ax.spines['left'].set_color('none')
                ax.axvline(ax.get_xlim()[0], ymin=0, ymax=1,
                       linewidth=1, linestyle='-', color="gray", clip_on=False)
        # 表格横线
        ax.axhline(self.change_coord(ax, 0, height)[1], xmin=0, xmax=1,
                   linewidth=1, linestyle='-', color="black", clip_on=False)
        # 最后一个图封闭线
        if (j == self.ncol - 1 or i * self.ncol + j == len(self.key) - 1) and k == 0:  # k =0 防止重复画线
            ymax = self.cal_table_height(0, title_loc, show_list)
            ax.axvline(ax.get_xlim()[1], ymin=0, ymax=ymax,
                       linewidth=1, linestyle='-', color="black", clip_on=False)

    def set_xtop_title_title(self, ax, i, j, k, title_loc, show_list=None):
        '''
        图片顶部表格标题, 如果不指定show_list, 则默认显示所有的key
        '''
        show_list = self.key[i * self.ncol + j] if show_list is None else show_list
        if (i + j == 0) or (i + j > 0 and self.key[i * self.ncol + j][k] != self.key[i * self.ncol + j - 1][k]):
            # 如果是第一个子图或者 这一层的当前标题与上一个图的标题不一样时
            height = self.cal_table_height(k, title_loc, show_list)
            xcoord, ycoord = self.change_coord(ax, title_loc[k]["font_xcoords"][f'{k}{i}{j}'],
                                               height - title_loc[k]['font_height'] - 5 / self.subplot_height)
            label = ax.text(x=xcoord, y=ycoord, s=show_list[k], rotation=title_loc[k]['angle'],
                            fontsize=title_loc[k]['font_size'], color="black", clip_on=False)

    def set_xtop_title(self, ax, i, j, title_loc, show_list=None):
        show_list = self.key[i * self.ncol + j] if show_list is None else show_list
        for k, name in enumerate(show_list):
            self.set_xtop_title_table(ax, i, j, k, title_loc, show_list)
            self.set_xtop_title_title(ax, i, j, k, title_loc, show_list)

    def set_xbottom_title(self, ax, i, j, title_loc):
        # if (j == 0) or (self.key[i * self.ncol + j][-1] != self.key[i * self.ncol + j - 1][-1] and j > 0):
        ax.set_xlabel(self.key[i * self.ncol + j][-1],
                      fontsize=title_loc[-1]["font_size"], color="black", rotation=title_loc[-1]['angle'])

    def set_xtitle(self, ax, i, j, title_loc):
        show_list = self.key[i * self.ncol + j][:-1] if len(self.key[0]) > 1 else self.key[i * self.ncol + j]
        if len(self.key[0]) > 1:
            self.set_xbottom_title(ax, i, j, title_loc)
        self.set_xtop_title(ax, i, j, title_loc, show_list)
        top = self.cal_table_height(0, title_loc, show_list) - 1
        bottom = self.cal_table_height(len(self.key[0]) - 1, title_loc) - 1
        self.adjust_picture(top, bottom)

    def set_title(self):
        title_loc = self.get_xtitle_loc()
        for i in range(self.nrow):
            for j in range(self.ncol):
                if i * (self.ncol) + j >= len(self.key):
                    break
                ax = self.get_ax(i, j)  # 单行和多行对子图的切片方式不一样
                ax.tick_params(axis="y", labelsize=8)
                # if i == 0 and j == 0:
                #     position = ax.set_ylabel(self.item_info["name"], fontsize=12)
                self.set_xtitle(ax, i, j, title_loc)


class Point_picture(Multi_picture):
    def __init__(self, item_info, key, data, picture_info):
        super().__init__(item_info, key, data, picture_info)

    def draw_picture(self):
        self.draw_point()
        self.set_axis()
        self.set_title()

    def set_axis(self):
        for i in range(self.nrow):
            for j in range(self.ncol):
                ax = self.get_ax(i, j)  # 单行和多行对子图的切片方式不一样
                if len(self.key[0])>1:
                    ax.set_xticks([])  # 隐藏所有底部坐标轴
                if j > 0 and i * (self.ncol) + j < len(self.key):
                    # ax.spines['left'].set_linewidth(0)####设置左边坐标轴的粗细
                    ax.spines['left'].set_color((230 / 255, 230 / 255, 230 / 255))
                    ax.spines['right'].set_color('none')
                    ax.set_yticks([])
                if i * (self.ncol) + j >= len(self.key):
                    # 多出来的没有数据的子图隐藏坐标轴
                    # 只显示每行第一个子图的纵坐标轴
                    ax.set_yticks([])
                    ax.set_xticks([])
                    ax.spines['right'].set_color('none')
                    if i * (self.ncol) + j > len(self.key):
                        ax.spines['left'].set_color('none')
                    ax.spines['top'].set_color('none')
                    ax.spines['bottom'].set_color('none')
                ax.locator_params(axis='y', nbins=20)
                ax.set_xlim(left=self.get_xlim(ax)[0], right=self.get_xlim(ax)[1])
                # 子图数据不一样，matplotlib自动设定的坐标轴也不一样，这里手动设置ylim让所有子图纵坐标都一样
                ax.set_ylim(bottom=self.get_ylim(ax)[0], top=self.get_ylim(ax)[1])

    def draw_point(self):
        for i in range(self.nrow):
            for j in range(self.ncol):
                if i * (self.ncol) + j >= len(self.key):
                    break
                ax = self.get_ax(i, j)
                self.draw_limit(ax)
                [x, y] = self.get_xy(self.key[i * self.ncol + j])
                color = self.get_hightlight_color(i, j)
                ax.plot(x, y, marker="o", markersize=self.point_size, linestyle="", color=color)


class Box_picture(Multi_picture):
    def __init__(self, item_info, key, data, picture_info):
        super().__init__(item_info, key, data, picture_info)
        self.base_color = "C0"
        

    def draw_picture(self):
        self.draw_box()
        self.set_axis()
        self.set_title()

    def draw_box(self):
        for i in range(self.nrow):
            for j in range(self.ncol):
                if i * (self.ncol) + j >= len(self.key):
                    break
                ax = self.get_ax(i, j)
                self.draw_limit(ax)
                [x, y] = self.get_xy(self.key[i * self.ncol + j])
                # todo, 限定箱体最大最小宽度
                width_r = 0.8
                # print("subplot_width is ", self.subplot_width)
                # print("width_r sum is ==========================",self.subplot_width * width_r)
                if self.subplot_width > 80:
                    width_r = 80 / self.subplot_width
                # print("width_r is ==========================", width_r)
                x0,xmax = ax.get_xlim()
                # print("old xlim is ", x0,xmax)
                color = self.get_hightlight_color(i, j)
                ax.boxplot(y, widths=width_r*(xmax-x0),
                           # positions=[1, 4],  # 放置在x轴的位置
                            notch=False, # 是否是凹口的形式展现箱线图，默认非凹口
                            vert=True, # 是否需要将箱线图垂直摆放，默认垂直摆放
                            meanline=True,  # 是否用线的形式表示均值，默认用点来表示
                            patch_artist=True,  # 是否填充箱体
                            showmeans=True, # 是否显示均值
                            showcaps=True, # 是否显示箱线图顶端和末端的两条线，默认显示
                            showfliers=True,  # 是否显示异常值
                            showbox=True, # 是否显示箱线图的箱体，默认显示
                            meanprops = {"color": "black", "linewidth": 1.2}, # 设置平均线的属性，如线的类型、粗细等
                            medianprops={"color": "red", "linewidth": 0.5},  # 设置中位数的属性，如线的类型、粗细等
                            boxprops={"facecolor": color, "edgecolor": "black", "linewidth": 0.5, "alpha":0.4},  # 设置箱体的属性，如边框色，填充色等
                            whiskerprops={"color": "black", "linewidth": 1.2, "alpha":0.8}, # 设置须的属性，如颜色、粗细、线的类型等
                            capprops={"color": "C0", "linewidth": 1.2}, # 设置箱线图顶端和末端线条的属性，如颜色、粗细等
                            sym="+",  # 异常点的形状)
                            )
                x0,xmax = ax.get_xlim()


def main(path, item, option_key, image_type="scater", image_hightlight=""):
    result = None
    csv2pd = CSV2pd(path)
    if not option_key or option_key==[""]:
        # 手动添加一列option
        csv2pd.df.insert(loc=0, column='--all--', value="---")
        option_key = ['--all--']
    group_data = csv2pd.group_data(option_key)
    group_key = csv2pd.group_key(group_data)
    if len(group_key)>100:
        return "factor too large"
    item_info = csv2pd.item_info(item)

    picture_info = {}
    if image_hightlight and image_hightlight in option_key:
        hightlight_color_index = option_key.index(image_hightlight)
        picture_info = {"hightlight_color_index": hightlight_color_index}

    if image_type=="scater":
        picture = Point_picture(item_info, group_key, group_data, picture_info)
    elif image_type=="box":
        picture = Box_picture(item_info, group_key, group_data, picture_info)
    result_file = BytesIO()
    picture.figure.savefig(result_file, format="png")
    # result_file.seek(0)
    # result = result_file.read()
    result = result_file.getvalue()
    # picture.figure.savefig(os.path.join(os.path.dirname(path), "picture.png"))
    # print("have save at ", os.path.join(os.path.dirname(path), "picture.png"))
    # plt.show()
    plt.close(fig=picture.figure)
    return result
