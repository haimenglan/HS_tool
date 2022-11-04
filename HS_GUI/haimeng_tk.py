import os
import sys
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.messagebox as tkmessage
import platform
import time
import math
import threading
import traceback

from PIL import Image, ImageTk


def get_china_time():
    local_time = time.localtime()
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = local_time[0], local_time[1], local_time[2], local_time[3], \
                                                        local_time[4], local_time[5]
    return f'{tm_year:02}年{tm_mon:02}月{tm_mday:02}日 {tm_hour:02}:{tm_min:02}:{tm_sec:02}'


# 通用函数
def color_change(r, g, b):
    return "#%02x%02x%02x" % (int(r), int(g), int(b))


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


class Haimeng_listbox_item:
    def __init__(self, frame_canvas, index, image_path, name, time, message, status):
        self.index = index
        self.frame_canvas = frame_canvas
        self.image_path = image_path
        self.name = name
        self.time = time
        self.message = message
        self.status = status

        self.screenheight = self.frame_canvas.winfo_screenheight()  # 屏幕高度
        self.screenwidth = self.frame_canvas.winfo_screenwidth()  # 屏幕宽度
        self.init_item_parameter()
        self.create_item()

    def init_item_parameter(self):
        self.status_color = {
            "在线": color_change(120, 248, 90),
            "离线": "gray",
            "未知": "red"
        }
        self.frame_bg = color_change(255, 255, 255)
        if platform.system() == "Windows":
            self.notice_ft = tkFont.Font(family='微软雅黑', size=14)  # 未读提示点的尺寸
            self.person_name_ft = tkFont.Font(family='微软雅黑', size=11)  # 联系人名字字体
            self.other_ft = tkFont.Font(family='微软雅黑', size=9)
        else:
            self.notice_ft = tkFont.Font(family='微软雅黑', size=12)  # 未读提示点的尺寸
            self.person_name_ft = tkFont.Font(family='微软雅黑', size=13)  # 联系人名字字体
            self.other_ft = tkFont.Font(family='微软雅黑', size=11)
            # item之间的分割线
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("my.TSeparator", background=color_change(230, 230, 230), relief="flat")
        # self.item_height = int(self.screenheight * 0.053)

    def create_item(self):
        # 创建item框架
        self.frame = tk.Frame(self.frame_canvas, bg=self.frame_bg)  # height=self.item_height)
        self.frame.grid(row=self.index, column=0, sticky="ewns")
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.notice_mark = tk.Label(self.frame, text="⚉", font=self.notice_ft, fg=self.frame_bg, bg=self.frame_bg)
        self.notice_mark.grid(row=1, column=0, sticky="w")
        # 显示头像 全局变量保持住 item_dict["image"]， 否则图片无法显示
        self.tk_image = change_photo(self.image_path, int(self.screenwidth * 0.025), is_zoomout=True, is_square=True)[0]
        self.tk_image_label = tk.Label(self.frame, bg=self.frame_bg, image=self.tk_image, cursor='hand2')
        self.tk_image_label.grid(row=0, column=1, rowspan=2, sticky="w")
        # 显示名字
        self.name_label = tk.Label(self.frame, text=self.name, font=self.person_name_ft, bg=self.frame_bg)
        self.name_label.grid(row=0, column=2, sticky="ws")
        # 显示信息
        self.message_label = tk.Label(self.frame, text=self.message, font=self.other_ft, bg=self.frame_bg, fg="gray")
        self.message_label.grid(row=1, column=2, sticky="wn")
        # 显示时间
        self.time_label = tk.Label(self.frame, text=self.time, font=self.other_ft, bg=self.frame_bg, fg="gray")
        self.time_label.grid(row=0, column=3, sticky="es")
        # 显示在线状态
        self.status_label = tk.Label(self.frame, text=self.status, font=self.other_ft, bg=self.frame_bg,
                                     fg=self.status_color[self.status])
        self.status_label.grid(row=1, column=3, sticky="en")
        # 显示分割线
        self.separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL, style="my.TSeparator")
        self.separator.grid(row=2, column=1, columnspan=3, sticky="wes")
        # 显示删除标记
        self.delete_mark = tk.Label(self.frame, text="x", font=self.notice_ft, fg=self.frame_bg, bg=self.frame_bg)
        self.delete_mark.grid(row=0, column=0, sticky="e")

        self.frame.update()
        self.item_height = self.frame.winfo_height()

    def change_my_index(self, index):
        self.index = index
        self.frame.grid_forget()
        self.frame.grid(row=index, column=0, sticky="nsew")

    def update_my_status(self):
        pass


class Haimeng_listbox:
    def __init__(self, root, width=None, height=None):
        """
        在父窗口上创建一个主框架，用来装listbox的画布和滚动条
        listbox的画布在主框架上创立，然后创建一个新的填充整个画布的框架，listbox的各个选项在此框架上创立
        listbox的每一个选项都是一个Haimeng_listbox_item对象
        """
        self.root = root
        self.screenwidth = self.root.winfo_screenwidth()  # 屏幕宽度
        self.screenheight = self.root.winfo_screenheight()  # 屏幕高度

        self.box_width = width  # 默认宽度
        self.box_height = height
        self.box_bg = color_change(255, 255, 255)  # 背景色
        self.select_color = color_change(238, 133, 48)  # 选择item色
        self.scroll_height = 0  # 滚动高度

        self.item_list = []  # item tk列表
        self.last_select = None  # 当前选择的item

        # list box 主框架
        self.frame_box = tk.Frame(root, bg=self.box_bg, width=self.box_width, height=self.box_height)
        self.frame_box_place()

    def grid(self, row=0, column=0, rowspan=None, columnspan=None, sticky=None, padx=0, pady=0):
        """
        在root上放置主框架
        """
        self.frame_box.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx,
                            pady=pady)
        self.canvas.update()
        self.canvas.bind("<Configure>", self.canvas_size_change)

    def frame_box_place(self):
        self.frame_box.rowconfigure(0, weight=1)
        self.frame_box.columnconfigure(1, weight=1)

        # 主框架添加画布
        self.canvas = tk.Canvas(self.frame_box, width=self.box_width, height=self.scroll_height, bg=self.box_bg,
                                scrollregion=(0, 0, self.screenwidth, self.scroll_height))
        self.canvas.grid(row=0, column=1, sticky="new")
        # 在左上角(0,0)位置添加滚动标记
        self.canvas.scan_mark(0, 0)
        # 画布上创建新框架，以支持小组件滚动
        self.frame_canvas = tk.Frame(self.canvas, bg=self.box_bg, width=self.box_width, height=self.scroll_height)
        self.frame_canvas.bind("<MouseWheel>", self.move_y_canvas)
        self.canvas.rowconfigure(0, weight=1)
        self.canvas.columnconfigure(0, weight=1)
        # 画布创建组件需要调用如下方法，参数包含添加的坐标，方向...
        self.canvas.create_window((0, 0), anchor="nw", window=self.frame_canvas, tags="frame_canvas")
        self.frame_canvas.columnconfigure(0, weight=1)  # 宽度自动填充
        # self.frame_canvas.grid(row=0,column=0,sticky="ew") 这一句用不到也没用
        # 主框架添左侧加滚动条
        self.sb_right = tk.Scrollbar(self.frame_box, orient=tk.VERTICAL, bg="gray")
        self.sb_right.grid(row=0, column=0, sticky="ns")
        self.sb_right.configure(command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.sb_right.set)

    def update_canvas_size(self, add_width, add_height):
        """
        增加画布的尺寸和滚动范围
        """
        self.scroll_height += add_height
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), self.scroll_height))
        self.canvas.update()
        self.canvas["height"] = self.scroll_height

    def change_item_index(self, old_index, new_index):  # 更新item原来的位置到新的位置
        if old_index >= len(self.item_list):  # 如果item原来的位置大于当前所有item的数量，说明没有这个item
            return None
        else:
            #  更新列表
            old_item = self.item_list.pop(old_index)  # 弹出旧的item
            self.item_list.insert(new_index, old_item)  # 将旧的item插入到新的位置
            # 更新位置
            if new_index > old_index:
                start, end = old_index, new_index + 1
            else:
                start, end = new_index, old_index + 1
            # 修改上次选择位置
            a = True
            for i in range(start, end):
                # 修改上次选择的位置
                if a and self.last_select is not None and self.last_select == self.item_list[i].index:
                    self.last_select = i
                    a = False
                # 修改新的item顺序
                self.item_list[i].change_my_index(i)

    def update_item_index(self, start_index, add_or_sub):
        """
        更新（从start_index往后的）选项的索引，全部+/-add_or_sub
        """
        if start_index < len(self.item_list):
            # 更新上一次选择的位置
            if self.last_select is not None:
                if self.last_select >= start_index and self.last_select < len(self.item_list):
                    self.last_select += add_or_sub
            # 更新选项索引
            i = start_index
            for each_item in self.item_list[start_index:]:  # 从start_index开始，
                each_item.change_my_index(i + add_or_sub)  # 更新每一项的坐标
                i += 1

    def insert(self, index, image_path, name, time, message, status, item_name=None):
        """
        添加选项到listbox， 参数为列表索引，头像路径，名字，时间，信息，在线状态，item_name是选项的字典索引，即账号
        1. 创建选项，更新画布尺寸
        2. 更新index后面的选项索引，添加选项到选项列表
        3. 为各个部件绑定事件
        """
        item = Haimeng_listbox_item(self.frame_canvas, index, image_path, name, time, message, status)
        if item_name is not None:
            item.item_name = item_name
        self.update_canvas_size(0, item.item_height)
        self.update_item_index(index, 1)
        self.item_list.insert(index, item)
        # 为插入的item绑定事件
        item_list = [item.frame, item.notice_mark, item.tk_image_label, item.name_label,
                     item.message_label, item.time_label, item.status_label, item.separator, item.delete_mark]
        for each_item in item_list:
            each_item.bind("<MouseWheel>", self.move_y_canvas)  # 双指滑动画布
            selecte_item_CMD = lambda event: self.selecte_item(item.index, item.item_name)
            each_item.bind("<ButtonPress-1>", selecte_item_CMD)  # 鼠标左键单击选项
            show_delete_mark_CMD = lambda event: self.show_delete_mark(item.delete_mark)
            each_item.bind("<Motion>", show_delete_mark_CMD)  # 鼠标进入选项
            hide_delete_mark_CMD = lambda event: self.hide_delete_mark(item.index, item.delete_mark)
            each_item.bind("<Leave>", hide_delete_mark_CMD)  # 鼠标离开选项
        delete_item_CMD = lambda item, event: self.delete_item(item)
        item.delete_mark.bind("<ButtonPress-1>", delete_item_CMD)  # 点击删除按钮
        return item

    def delete_item(self, item, event=None):
        """
        删除选项：
          1. 改变被删除选项后面的选项索引
          2. 更新画布尺寸
          3. 销毁选项框架, 并将选项从列表中弹出
        """
        if item.index == self.last_select:
            self.unselect_item()  # 重置选中状态，主要是为了还原被选中选项的上一个选项的分割线
            self.last_select = None
        item.frame.destroy()
        self.update_item_index(item.index + 1, -1)
        self.update_canvas_size(0, -item.item_height)
        self.item_list.pop(item.index)

    def unselect_item(self):
        if self.last_select is not None:
            if self.last_select > 0:  # 第0个上面没有分割线
                self.item_list[self.last_select - 1].separator.grid(row=2, column=1, columnspan=3, sticky="wes")
            self.item_list[self.last_select].separator.grid(row=2, column=1, columnspan=3, sticky="wes")
            item = self.item_list[self.last_select]
            item.message_label.configure(fg="gray", bg=self.box_bg)
            item.time_label.configure(fg="gray", bg=self.box_bg)
            item.notice_mark.configure(fg=self.box_bg, bg=self.box_bg)
            item.delete_mark.configure(fg=self.box_bg, bg=self.box_bg)
            item.frame.configure(bg=self.box_bg)
            item.tk_image_label.configure(bg=self.box_bg)
            item.name_label.configure(bg=self.box_bg)
            item.status_label.configure(bg=self.box_bg)

    def selecte_item(self, ID, item_name=None):
        if self.last_select is not None:
            self.unselect_item()
        if ID > 0:
            self.item_list[ID - 1].separator.grid_forget()
        item = self.item_list[ID]
        item.separator.grid_forget()
        item.message_label.configure(fg="white", bg=self.select_color)
        item.time_label.configure(fg="white", bg=self.select_color)
        item.notice_mark.configure(fg=self.select_color, bg=self.select_color)
        item.delete_mark.configure(bg=self.select_color)

        item.frame.configure(bg=self.select_color)
        item.tk_image_label.configure(bg=self.select_color)
        item.name_label.configure(bg=self.select_color)
        item.status_label.configure(bg=self.select_color)
        self.last_select = ID

    def show_delete_mark(self, mark):
        mark["fg"] = "red"

    def hide_delete_mark(self, index, mark):
        if self.last_select == index:
            mark["fg"] = self.select_color
        else:
            mark["fg"] = self.box_bg

    # 事件响应
    # 当画布的宽度变化时, 画布框架的宽度与其保持一致，因为画布内的所有组件，其size均无法自动调节
    def canvas_size_change(self, event):
        self.canvas.itemconfigure("frame_canvas", width=self.canvas.winfo_width())

    # 滚动画布
    def move_y_canvas(self, event):
        """
        event.delta >0 : 双指上滑/左滑
        self.canvas.scan_dragto(x_step, y_step, gain=1)：
          将画布从标记的scan_mark位置拖到 (新的坐标-mark坐标)*gain位置，这里的位置是指画布坐标
        """
        self.canvas.scan_mark(0, int(self.canvas.canvasy(0)))  # int(self.canvas.canvasx(0))
        self.canvas.scan_dragto(0, int(self.canvas.canvasy(0)) + event.delta * 5, gain=1)


class Haimeng_Canvas(tk.Canvas):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

    # 自定义raise方法，让画布可以置顶显示
    def my_tkraise(self, aboveThis=None):
        """Raise this widget in the stacking order."""
        self.tk.call('raise', self._w, aboveThis)


class Haimeng_chat_window:
    def __init__(self, root, bg=None):
        """
        在root上添加一个画布和滚动条，画布上用以添加消息，所有的消息显示都是画出来的
        """
        self.root = root
        self.root.update()
        self.screenwidth = self.root.winfo_screenwidth()  # 屏幕宽度
        self.screenheight = self.root.winfo_screenheight()  # 屏幕高度
        self.canvas_winfo_width = self.root.winfo_width()
        self.canvas_winfo_height = self.root.winfo_height()
        self.canvas_bg = bg
        self.init_canvas_param()
        if platform.system() == "Windows":
            self.ft_message = tkFont.Font(family="微软雅黑", size=11)  # 信息字体
            self.time_ft = tkFont.Font(family='微软雅黑', size=10)  # 未读提示点的尺寸
            self.avatar_width = int(self.screenwidth * 0.022)  # 好友头像宽度
        else:
            self.ft_message = tkFont.Font(family="DengXian Regular", size=13)  # 信息字体
            self.time_ft = tkFont.Font(family='微软雅黑', size=12)  # 未读提示点的尺寸
            self.avatar_width = int(self.screenwidth * 0.025)  # 好友头像宽度
        self.chat_canvas = Haimeng_Canvas(self.root, bg=self.canvas_bg,
                                          highlightthickness=0,
                                          highlightcolor=self.canvas_bg,
                                          scrollregion=(0, 0, self.canvas_winfo_width, 0))
        # 主框架添左侧加滚动条
        self.sb_right = tk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.sb_right.configure(command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.sb_right.set)

    def init_canvas_param(self):
        self.WINDOW_AVATAR_X = 20
        self.AVATAR_MESSAGE_X = 8
        self.MESSAGE_MESSAGE_Y = 10
        self.TEXT_RECTANGLE_X = 8
        self.TEXT_RECTANGLE_Y = 8
        self.image_zoom_ratio = 0.1256

        self.canvas_ystart_location = 0
        self.canvas_yend_location = 0
        self.canvas_max_message = 30
        self.text_max_width = 40

        self.avatar_path_list = []
        self.avatar_list = []
        self.ID = 0
        self.canvas_message_list = []
        self.image_list = []
        self.canvas_time = None
        self.lock = threading.Lock()

    def grid(self, row_=0, column_=0, rowspan=None, columnspan=None, sticky=None, padx=0, pady=0):
        """
        放置画布，绑定画布尺寸改变事件
        放置之后再绑定，因为放置前的尺寸是1，放置后尺寸改变也会触发此事件
        绑定双指滑动画布事件
        """
        self.root.rowconfigure(row_, weight=1)
        self.root.columnconfigure(column_, weight=1)
        self.chat_canvas.grid(row=row_, column=column_, rowspan=rowspan, columnspan=columnspan, sticky=sticky,
                              padx=padx, pady=pady)
        self.sb_right.grid(row=row_, column=column_ + 1, sticky="ns")
        self.canvas_winfo_width, self.canvas_winfo_height = self.get_chat_canver_winfo_size()
        self.chat_canvas.bind("<Configure>", self.chat_canvas_size_change)
        self.x_step = 0
        self.y_step = 0
        self.chat_canvas.scan_mark(self.x_step, self.y_step)
        self.chat_canvas.bind("<MouseWheel>", self.move_y_canvas)

    def tkraise(self):
        """
        画布置顶显示
        """
        self.chat_canvas.my_tkraise()
        self.sb_right.tkraise()

    def get_chat_canver_winfo_size(self):
        """
        获取画布尺寸
        """
        self.chat_canvas.update()
        return self.chat_canvas.winfo_width(), self.chat_canvas.winfo_height()

    def chat_canvas_size_change(self, event):
        """
        画布尺寸改变：
            凡是在右边的消息，一律跟着画布改变的尺寸移动到画布最右边
            时间保持在画布中间位置
        """
        canvas_winfo_width, canvas_winfo_height = self.get_chat_canver_winfo_size()
        move_x_step = canvas_winfo_width - self.canvas_winfo_width
        # move_y_step = canvas_winfo_height - self.canvas_winfo_height
        if math.fabs(move_x_step) > 20:
            self.canvas_winfo_width, self.canvas_winfo_height = self.get_chat_canver_winfo_size()
            for each_message in self.canvas_message_list:
                # coords = self.chat_canvas.coords(each_item) 获取对象尺寸
                if each_message["xside"] == "e":
                    # todo 向左移动错误问题
                    for each_item in each_message["item_list"]:
                        self.chat_canvas.move(each_item, move_x_step, 0)  # 此函数给的坐标是 移动偏量坐标, 即从原来的坐标增加x1,y1
                        # self.chat_canvas.update()
                if each_message["time"] is not None:
                    self.chat_canvas.move(each_message["time"], move_x_step / 2, 0)
            self.chat_canvas.update()

    def move_y_canvas(self, event):
        """
        双指滑动画布
        """
        speed = 20
        if event.delta > 0:  # 画布和双指下移，滚动条上移
            # print("上移",self.chat_canvas.canvasy(0)) # 窗口坐标为0的位置对应的画布的坐标
            # if self.chat_canvas.canvasy(0)>0:  # 禁止画布超出窗口的（0，0）位置，此函数是获取窗口0位置对应的画布坐标
            self.y_step = -int(self.chat_canvas.canvasy(0)) + speed  # 上移最大值为20
        if event.delta < 0:  # 画布和双指上移，滚动条下移,
            # print("下移",self.chat_canvas.canvasy(0))
            self.y_step = -int(self.chat_canvas.canvasy(0)) - speed
        # 将画布从标记的scan_mark位置拖到 (新的坐标-mark坐标)*gain 位置(这里的位置指的是窗口坐标)
        self.chat_canvas.scan_dragto(self.x_step, self.y_step, gain=1)

    def create_time(self, canvas_winfo_width, xside, yside, **kwargs):
        """
        在画布中间创建时间
        """
        self.canvas_time = time.time()
        if "contact_time" in kwargs:
            time_str = kwargs["contact_time"]
        else:
            time_str = get_china_time()
        # print("插入的时间是++++++++++++++++++++++", time_str)
        x1 = canvas_winfo_width / 2
        if yside == "s":
            y1 = self.canvas_yend_location + self.MESSAGE_MESSAGE_Y
            font_height = self.MESSAGE_MESSAGE_Y
            self.canvas_yend_location += font_height
        else:
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y
            font_height = -self.MESSAGE_MESSAGE_Y
            self.canvas_ystart_location -= font_height
        return self.chat_canvas.create_text(x1, y1, text=time_str, fill="gray")

    def create_name(self, canvas_winfo_width, xside, yside, **kwargs):
        """
        创建用户名字
        """
        if xside == "w":
            x1 = self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X
        else:
            x1 = canvas_winfo_width - (self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X)
        if yside == "s":
            y1 = self.canvas_yend_location + self.MESSAGE_MESSAGE_Y
        else:
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y
        text_name = self.chat_canvas.create_text(x1, y1, text=kwargs["name"], fill="gray")  # 中心位置
        font_size = self.chat_canvas.bbox(text_name)
        font_width = font_size[2] - font_size[0]
        font_height = font_size[3] - font_size[1]
        if xside == "w":
            x_move = font_width / 2
        else:
            x_move = - font_width / 2
        if yside == "n":
            y_move = -font_height / 2
        else:
            y_move = font_height / 2
        self.chat_canvas.move(text_name, x_move, y_move)
        self.chat_canvas.update()
        if yside == "s":
            self.canvas_yend_location += font_height
        return text_name, font_height

    def create_avatar(self, canvas_winfo_width, avatar_path, xside, yside):
        """
        创建用户头像
        """
        if avatar_path not in self.avatar_path_list:
            self.avatar_path_list.append(avatar_path)
            avatar = change_photo(avatar_path, self.avatar_width, is_zoomout=True, is_square=True)[0]
            self.avatar_list.append(avatar)
        index = self.avatar_path_list.index(avatar_path)
        x1, y1 = 0, 0
        if xside == "w":
            x1 = self.WINDOW_AVATAR_X + self.avatar_width / 2
        else:
            x1 = canvas_winfo_width - (self.WINDOW_AVATAR_X + self.avatar_width / 2)
        if yside == "s":
            y1 = self.MESSAGE_MESSAGE_Y + self.canvas_yend_location + self.avatar_width / 2
        else:
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y - self.avatar_width / 2
        return self.chat_canvas.create_image((x1, y1), image=self.avatar_list[index])  # x1,y1 是 图片的中心位

    def open_link(self, event, link):
        """
        发送图片/文件绑定链接
        # todo如果是图片直接打开文件
        """
        yesno = tk.messagebox.askyesno("打开所在路径(yes)或打开文件(no)", f"文件位置是：\n{link}")
        if platform.system() != "Windows":
            os.system(f"open '{os.path.dirname(link)}'")
            # if yesno:
            #     os.system(f"open '{os.path.dirname(link)}'")
            # else:
            #     os.system(f"open '{link}'")

    def create_link(self, image, link):
        open_link_CMD = lambda event: self.open_link(event, link)
        self.chat_canvas.tag_bind(image, "<ButtonPress-1>", open_link_CMD)

    def get_font_height_width(self, font_):
        font_size = self.chat_canvas.bbox(font_)
        font_width = font_size[2] - font_size[0]
        font_height = font_size[3] - font_size[1]
        return font_width, font_height

    def create_image(self, canvas_winfo_width, xside, yside, **kwargs):
        """
        显示发送/接收图片/文件
        """
        if "image_width" in kwargs:
            width = kwargs["image_width"]
        else:
            width = int(self.screenwidth * self.image_zoom_ratio)
        image_tk, image_size = change_photo(kwargs["image_path"], width,
                                            is_zoomout=False, is_square=False)
        self.image_list.append(image_tk)
        x1, y1 = 0, 0
        if xside == "w":
            x1 = self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + image_size[0] / 2
        elif xside == "e":
            x1 = canvas_winfo_width - (
                    self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + image_size[0] / 2)
        if yside == "s":
            y1 = self.MESSAGE_MESSAGE_Y + self.canvas_yend_location + image_size[1] / 2
        else:
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y - image_size[1] / 2
        image = self.chat_canvas.create_image((x1, y1), image=self.image_list[-1])
        if "link" in kwargs:
            self.create_link(image, kwargs["link"])
        if "persent" in kwargs:
            file_name = self.chat_canvas.create_text(x1, y1,
                                                     text=kwargs["persent"].replace(kwargs["persent"].split(" ")[-1],
                                                                                    ""), fill="gray")
            file_name_width, file_name_height = self.get_font_height_width(file_name)
            persent = self.chat_canvas.create_text(x1, y1 + file_name_height, text=kwargs["persent"].split(" ")[-1],
                                                   fill="gray")
            # print("文件百分比是", kwargs["persent"].split(" ")[1] )
            persent_widht, persent_height = self.get_font_height_width(persent)

            if xside == "w":
                x_move = file_name_width / 2 + image_size[0] / 2
            else:
                x_move = - file_name_width / 2 - image_size[0] / 2
            # if yside == "n":
            #     y_move = -(file_name_height+persent_height) / 2
            # else:
            #     y_move = (file_name_height+persent_height) / 2
            y_move = 0
            self.chat_canvas.move(file_name, x_move, y_move)
            self.chat_canvas.move(persent, x_move, y_move)
            self.chat_canvas.update()
            return [image, image_size[1], persent, file_name]  # x1,y1 是 图片的中心位
        return [image, image_size[1]]
        # todo add link

    # size1 = self.ft_message.measure("，")  # 单个字符的像素宽度19
    # size2 = self.ft_message.measure("蓝")  # 一个字符的像素宽度19
    # size3 = self.ft_message.measure("海")  # 一个字符的像素宽度19
    # size4 = self.ft_message.measure("蓝海")  # 两个字符的像素宽度37
    # size5 = self.ft_message.measure("蓝海梦")  # 三个56 = 37+19
    # size6 = self.ft_message.measure("蓝海梦啊")  # 三个74 = 37+37
    # size7 = self.ft_message.measure("蓝海梦啊abc")  # 106 = 19*4 + 3*10
    # size8 = self.ft_message.measure("ab")  # 21
    # size9 = self.ft_message.measure("a")  # 10
    # size10 = self.ft_message.measure("abc")  # 30
    # size11 = self.ft_message.measure("abcd")  # 41
    # print(size1, size2, size3, size4, size5, size6, size7, size8, size9, size10, size11)
    def get_text_width_height_(self, data):
        """
        根据文字的数量来计算text框的宽度和高度
        """
        char_unit = self.ft_message.measure("1")  # mac中单个字符的像素宽度,相当于text设置的width=1的宽度
        max_width = self.text_max_width
        max_size = max_width * char_unit  # text所能显示的最大宽度
        text_width = 0
        text_height = 1
        start_index = 0
        end_index = 0
        if self.ft_message.measure(data) < max_size:
            text_width = self.ft_message.measure(data) / char_unit
            if text_width > int(text_width):
                text_width = int(text_width) + 1
            text_height = 1
        else:
            for each_char in data:
                end_index += 1
                line_size = self.ft_message.measure(data[start_index:end_index])
                if line_size > max_size:
                    start_index = end_index
                    text_height += 1
        if text_height > 1:
            text_width = max_width
        return text_width, text_height

    def get_text_width_height(self, data):
        text_width = 0
        text_height = 0
        for each_data in data.split("\n"):
            if each_data != '':
                width, height = self.get_text_width_height_(each_data)
                if width > text_width:
                    text_width = width
                text_height += height
        text_height += data.count("\n\n")  # 空行需要加1
        return int(text_width), int(text_height)

    def create_text(self, canvas_winfo_width, xside, yside, message):
        x1, y1 = 0, 0
        text_color = "white"
        if xside == "w":
            x1 = self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + self.TEXT_RECTANGLE_X
        else:
            x1 = canvas_winfo_width - (
                    self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + self.TEXT_RECTANGLE_X)
            text_color = "orange"
        if yside == "s":
            y1 = self.canvas_yend_location + self.MESSAGE_MESSAGE_Y + self.TEXT_RECTANGLE_Y
        else:
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y - self.TEXT_RECTANGLE_Y

        text_coord = (x1, y1)
        text_width_set, text_height_set = self.get_text_width_height(message)
        # 根据计算得到的长和宽创建text组件
        text = tk.Text(self.chat_canvas, width=text_width_set, height=text_height_set,
                       background=text_color,
                       borderwidth=0,
                       highlightthickness=0,
                       insertborderwidth=0,
                       highlightbackground=text_color,
                       highlightcolor=text_color,
                       font=self.ft_message
                       )
        text.bind("<MouseWheel>", self.move_y_canvas)
        text.insert(tk.END, message)
        text_ID = self.chat_canvas.create_window(text_coord, anchor="nw",
                                                 window=text, tags="text")  # todo 尝试隐形创建
        text.update()  # 必须在text insert内容后才能得到text的宽度
        # text_width = text.winfo_width() 这种方法只能获取窗口所能看到的宽度，当text创建在画布滚动范围底部（超出窗口之外时），获取的宽度为1不正确
        # text_height = text.winfo_height()
        text_size = self.chat_canvas.bbox(text_ID)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]
        if xside == "e":
            # 获取到Text的像素宽度后，再将它移到圆角矩形的内部
            x1 = x1 - text_width
        if yside == "n":
            y1 = y1 - text_height
        text_coord = (x1, y1)
        self.chat_canvas.coords(text_ID, text_coord)
        # self.chat_canvas.move(text_ID,text_coord[0],text_coord[1])
        text.update()  # 更新它让它更快的移动
        return text_ID, text_width, text_height

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        # my_rectangle = round_rectangle(50, 50, 150, 100, radius=20, fill="blue")
        return self.chat_canvas.create_polygon(points, **kwargs, smooth=True)

    def create_round_rectangle(self, canvas_winfo_width, text_width, text_height, xside, yside):
        # 创建离头像左侧10个像素点，与头像水平位置齐平的圆角矩形框
        x1, y1, x2, y2 = 0, 0, 0, 0
        round_rectangle_color = 'white'
        if xside == "w":
            x1 = self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X
            x2 = self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + text_width + self.TEXT_RECTANGLE_X * 2
        else:
            x1 = canvas_winfo_width - (
                    self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X + text_width + self.TEXT_RECTANGLE_X * 2)
            x2 = canvas_winfo_width - (self.WINDOW_AVATAR_X + self.avatar_width + self.AVATAR_MESSAGE_X)
            round_rectangle_color = 'orange'
        if yside == "s":
            y1 = self.MESSAGE_MESSAGE_Y + self.canvas_yend_location
            y2 = self.MESSAGE_MESSAGE_Y + self.canvas_yend_location + text_height + self.TEXT_RECTANGLE_Y * 2
        else:
            y2 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y
            y1 = self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y - text_height - self.TEXT_RECTANGLE_Y * 2
        round_rectangle = self.round_rectangle(x1=x1,
                                               y1=y1,
                                               x2=x2,
                                               y2=y2,
                                               fill=round_rectangle_color)  # x1,y1是中心位置
        return round_rectangle

    def create_content(self, canvas_winfo_width, xside, yside, message, **kwargs):
        item_list = []
        new_add_height = 0
        if "image_path" not in kwargs:  # 如果不是插入图片
            textID, text_width, text_height = self.create_text(canvas_winfo_width, xside, yside, message)
            round_rectangle = self.create_round_rectangle(canvas_winfo_width, text_width, text_height, xside, yside)
            # 刷新位置
            new_add_height += text_height + self.MESSAGE_MESSAGE_Y + self.TEXT_RECTANGLE_Y * 2
            item_list += [textID, round_rectangle]
        else:
            create_image_result = self.create_image(canvas_winfo_width, xside, yside, **kwargs)
            if len(create_image_result) == 2:
                image, image_height = create_image_result[0], create_image_result[1]
                item_list += [image]
            else:
                image, image_height, persent, file_name = \
                    create_image_result[0], create_image_result[1], create_image_result[2], create_image_result[3]
                item_list += [image, persent, file_name]
            new_add_height += image_height + self.MESSAGE_MESSAGE_Y
        return item_list, new_add_height

    def move_name_location(self, avatar, text_name, text_name_height, new_add_height):
        if text_name is not None:
            name_move_y = -(new_add_height - self.MESSAGE_MESSAGE_Y)
            self.chat_canvas.move(text_name, 0, name_move_y)
            self.canvas_ystart_location -= text_name_height
        avatar_move_y = -(new_add_height - self.MESSAGE_MESSAGE_Y - self.avatar_width)
        self.chat_canvas.move(avatar, 0, avatar_move_y)

    def add_item_to_list(self, xside, yside, item_list, text_time, new_add_height):
        """
        item_dict包含了每一条消息的方向、画布组件、创建时间
        """
        item_dict = {"ID": self.ID, "xside": xside, "yside": yside, "item_list": item_list, "time": text_time}
        if yside == "n":
            item_dict["ystart"] = self.canvas_ystart_location
            item_dict["yend"] = self.canvas_ystart_location + new_add_height
            self.canvas_message_list.insert(0, item_dict)
        else:
            item_dict["ystart"] = self.canvas_yend_location
            item_dict["yend"] = self.canvas_yend_location + new_add_height
            self.canvas_message_list.append(item_dict)
        self.ID += 1
        return item_dict

    def delete_redundant_message(self):
        message_num = len(self.canvas_message_list)
        if message_num > self.canvas_max_message:
            try:
                i = 0
                for each_message in self.canvas_message_list[:message_num - self.canvas_max_message]:
                    # self.canvas_message_list.remove(each_message)
                    self.canvas_message_list.pop(i)
                    i += 1
                    for each_item in each_message["item_list"]:
                        self.chat_canvas.delete(each_item)
                # 前面的都删除了，从第0项开始显示
                self.canvas_ystart_location = self.canvas_message_list[0]["ystart"] - self.MESSAGE_MESSAGE_Y
            except:
                pass

    def update_canvas_location(self, yside, canvas_winfo_width, new_add_height):
        """
        更新画布顶部或底部位置
        更新画布滚动范围
        检查是否删除多余消息
        拖动画布到最底部
        """
        if yside == "n":
            self.canvas_ystart_location -= new_add_height
        else:
            self.canvas_yend_location += new_add_height
            self.delete_redundant_message()  # 删除多余的消息以节省内存提高速度
        # 重定义滚动范围
        self.chat_canvas.configure(scrollregion=(0, self.canvas_ystart_location - self.MESSAGE_MESSAGE_Y,
                                                 canvas_winfo_width,
                                                 self.canvas_yend_location + self.MESSAGE_MESSAGE_Y))
        # 如果是向下插入信息则移动画布到最底部
        if yside == "s":
            self.chat_canvas.scan_dragto(0, -(self.canvas_yend_location + self.MESSAGE_MESSAGE_Y), gain=1)
        # print("我的位置是", self.canvas_yend_location)
        self.chat_canvas.update()

    def get_item_index(self, ID):
        return [i for i, d in enumerate(self.canvas_message_list) if d["ID"] == ID][0]

    def create_message(self, avatar_path, xside, yside, message, **kwargs):
        """
        1. 创建头像
        2. 画聊天气泡
        3. 创建text 或者 图片
        4. 创建圆角矩形背景
        5. item_dict包含这一条消息的方向、画布组件列表(item_list)、创建时间信息等：
            item_dict = {"ID":xxx, "xside": xside, "yside": yside, "item_list": item_list, "time": text_time, "y_start":xxx, "y_end":xxx}
            
            item_list 有三种可能：
            1）头像+text框+消息矩形框
            2）头像+图片
            3）头像+图片+百分比+文件名

            item_list = [[text_name,] avatar] + [textID, round_rectangle] or [image, persent, file_name]
        6. self.canvas_message_list列表则存储所有的item_dict
        7. 返回的是当前创建的消息的ID，ID 是标记每一条消息的序号，每发送一条消息，ID+1， 不论该消息是否被删除（移出消息列表）
        """
        # self.lock.acquire()  # 可能会导致死锁
        print("我在添加消息")
        try:
            canvas_winfo_width, canvas_winfo_height = self.get_chat_canver_winfo_size()
            item_list = []
            text_time, text_name = None, None
            text_name_height = 0
            # 先创建时间和名字，因为这会影响到后面创建头像及内容的位置
            if "contact_time" in kwargs or self.canvas_time is None or time.time() - self.canvas_time > 180:
                text_time = self.create_time(canvas_winfo_width, xside, yside, **kwargs)
            if "name" in kwargs:
                text_name, text_name_height = self.create_name(canvas_winfo_width, xside, yside, **kwargs)
                item_list.append(text_name)
            avatar = self.create_avatar(canvas_winfo_width, avatar_path, xside, yside)
            # 计算发送内容需要的高度（像素点）
            content_list, new_add_height = self.create_content(canvas_winfo_width, xside, yside, message, **kwargs)
            if yside == "n":  # 倒着插入的名字需要调整位置
                self.move_name_location(avatar, text_name, text_name_height, new_add_height)
            item_list += [avatar] + content_list
            item_dict = self.add_item_to_list(xside, yside, item_list, text_time, new_add_height)
            self.update_canvas_location(yside, canvas_winfo_width, new_add_height)
            # self.lock.release()
            print("添加完成")
            return item_dict["ID"]
        except Exception as e:
            print("创建信息出错", str(e))
            traceback.print_exc()
            # self.lock.release()

    def delete_message(self, message_ID):
        """
        隐藏一条消息：
        1. 从画布删除该消息包含的组件
        2. 更新画布尺寸， 线程锁的作用是，防止尺寸未更新完成，又有别的消息删除或者插入，导致位置不正确
        """
        # self.lock.acquire()
        print("我在删除图标")
        try:
            message_index = self.get_item_index(message_ID)
            item_dict = self.canvas_message_list[message_index]
            canvas_winfo_width, canvas_winfo_height = self.get_chat_canver_winfo_size()
            for each_item in item_dict["item_list"]:
                self.chat_canvas.delete(each_item)
            new_add_height = -(item_dict["yend"] - item_dict["ystart"])
            if self.canvas_message_list[message_index + 1:]:  # 如果后面还有信息, 把后面的消息位置挪动到前面
                for each_message in self.canvas_message_list[message_index + 1:]:
                    for each_item in each_message["item_list"]:
                        self.chat_canvas.move(each_item, 0, new_add_height)  # 此函数给的坐标是 移动偏量坐标, 即从原来的坐标增加x1,y1
                    if each_message["time"] is not None:
                        self.chat_canvas.move(each_message["time"], 0, new_add_height / 2)
                self.chat_canvas.update()
            self.canvas_message_list.pop(message_index)  # 彻底删除消息
            self.update_canvas_location("s", canvas_winfo_width, new_add_height)
            # self.lock.release()
            print("删除完成")
        except Exception as e:
            print("创建信息出错", str(e))
            # self.lock.release()


if __name__ == "__main__":
    root = tk.Tk()
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    root_width = int(screenwidth * 0.45)
    root_height = int(screenheight * 0.5)
    root.geometry('%sx%s' % (root_width, root_height))
    root.geometry('+%s+%s' % (int((screenwidth - root_width) / 2),
                              int((screenheight - root_height) / 2)))  # 在屏幕中间开启窗口

    # list_box 测试程序
    # haimeng_listbox = Haimeng_listbox(root,300,1000)
    # haimeng_listbox.grid(0,0)
    # haimeng_listbox.insert(0,"/Users/15400155/Desktop/HealthSensingToolX/res/DUT.png","蓝海梦","19:00","你好","在线")
    # haimeng_listbox.insert(1,"/Users/15400155/Desktop/HealthSensingToolX/res/DUT.png","蓝海梦","19:00","你好","在线")

    # chat_window测试程序
    haimeng_chat_window = Haimeng_chat_window(root, bg=color_change(235, 235, 235))
    haimeng_chat_window.grid(0, 0, sticky="ewns")

    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "s", "第1", name="小蓝")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "s", "第2", name="小蓝")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "n", "第3\n你好\n我聊", name="小蓝")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "n", "第4", name="小蓝")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "e", "s", "第5", name="小红")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "e", "s", "第6", name="小红")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "e", "s", "第7", name="小红")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "e", "n", "第8\n第4\n第4", name="小红")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "n", "第9")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "n", "finish!")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "n", "",
                                       name="小明",
                                       image_path="C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       link="C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png")
    haimeng_chat_window.create_message("C:/Users/蓝海梦/Desktop/pytho_project/res/person/nobody.png",
                                       "w", "s", "",
                                       name="蓝海梦",
                                       image_path="C:/Users/蓝海梦/Desktop/pytho_project/res/person/haimeng.png",
                                       link="C:/Users/蓝海梦/Desktop/pytho_project/res/person/haimeng.png")

    root.mainloop()