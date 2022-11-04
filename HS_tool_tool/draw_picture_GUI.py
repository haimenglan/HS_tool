import tkinter as tk
from tkinter import ttk

import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import random
import platform
import time
import re
if platform.system() == "Windows":
    import ctypes
    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)


class MenuListBox:
    def __init__(self, master, menu_list):
        """
        创建数据分类(SN/Station/config...)菜单列表框
        """
        self.master = master
        self.Menu_list = menu_list
        self.color_by_string_var = tk.StringVar()
        self.color_by_string_var.set(self.Menu_list[0])
        self.color_by_menu = tk.OptionMenu(self.master, self.color_by_string_var, # "all_data",
                                            *self.Menu_list)
        if platform.system() == "Windows":
            xx_list_box_height = 20
        else:
            xx_list_box_height = 13
        self.xx_list_box = tk.Listbox(master, selectmode="extended", width=35, height=xx_list_box_height)
        self.xx_sb_ver = ttk.Scrollbar(master, orient="vertical")
        self.xx_sb_ver.configure(command=self.xx_list_box.yview)  # 配置垂直滚动条
        self.xx_list_box.config(yscrollcommand=self.xx_sb_ver.set)

    def grid(self, **kw):
        self.color_by_menu.grid(**kw)
        kw.pop("sticky")
        row = kw["row"]+1
        kw.pop("row")
        self.master.rowconfigure(row, weight=1)
        self.master.columnconfigure(kw["column"], weight=1)
        self.xx_list_box.grid(row=row, sticky="wnse", **kw)
        column = kw["column"]+1
        kw.pop("column")
        self.xx_sb_ver.grid(row=row, column=column, sticky="ns", **kw)

    @staticmethod
    def generate_color():
        """生成tk颜色值"""
        r = float(random.randint(1, 254) / 256)
        g = float(random.randint(1, 254) / 256)
        b = float(random.randint(1, 254) / 256)
        return f"#{int(r * 256):02x}{int(g * 256):02x}{int(b * 256):02x}"

    def generate_color_dict(self, option_list):
        """
        根据给的筛选项，为每一个项目生成不同的颜色值（支持tk的颜色值), 并保存到字典color_dict
        """
        color_dict = {}
        for each_option in option_list:
            tk_color = self.generate_color()
            current_time = time.time()
            while tk_color in color_dict and (time.time()-current_time)<5:
                tk_color = self.generate_color()
            color_dict[each_option] = tk_color
        return color_dict

    def insert_xx_list_box(self, option_list, color_dict):
        """
        显示筛选项list box
        option_list 包含每个选项名字的列表，color_dict：每个选项名字对应的颜色 字典
        """
        self.xx_list_box.delete(0, tk.END)
        i = 0
        for each_xx in option_list:
            self.xx_list_box.insert(i, each_xx)
            self.xx_list_box.itemconfigure(i, bg=color_dict[each_xx],
                                           selectbackground=color_dict[each_xx],
                                           selectforeground="white")
            i += 1


class ColorByMenuListBox(MenuListBox):
    def __init__(self, master, menu_list):
        super().__init__(master, menu_list)
        # self.xx_list_box.bind("<ButtonPress-1>", self.click_list_box)
        # self.xx_list_box.bind("<KeyPress-Up>", self.click_list_box)
        # self.xx_list_box.bind("<KeyPress-Down>", self.click_list_box)
        self.current_select = ["all_data"]  # 当前listbox的选中项目
        self.current_option_list = ["all_data"]  # 当前listbox存在的所有项目
        self.option_dict = {}  # {”Serialnumber": [SN1,SN2,SN3]}
        self.color_dict = {}  # 颜色字典 {”xx_name":颜色值 }

    @property
    def is_select_all(self):
        return True if len(self.current_select) == len(self.current_option_list) else False

    def click_list_box(self, event=None):
        """
        获取当前选择的筛选项each_xx(SN/station/config)
        """
        self.current_select = [self.current_option_list[i] for i in self.xx_list_box.curselection()]

    def get_item_xx_name(self, option_name, select_item):
        """
        option_name 是xx_list_box的选择项目：f'{each_name}  {each_xx}'
        select_item 是选择的测项列表
        此函数是要从给定的选择项，分离出测试项和each_xx
        """
        for each_item in select_item:
            item_name = "" if len(select_item) == 1 else each_item
            if option_name.find(item_name) == 0:  # 找到选择的测试项
                for each_xx in self.option_dict[self.color_by_string_var.get()]:
                    if each_xx in option_name:  # 找到 each_xx
                        return [each_item, each_xx]

    def reflesh_option_list(self, select_item, option_dict, use_default_color=True):
        """
        选择的测试项改变时，重新生成对应的筛选项目列表和颜色空间：
        total_option_list 是所有菜单(all, Station ID...)包含的选项
        self.current_option_list 是当前选择菜单包含的选项
        """
        self.option_dict = option_dict
        if len(select_item) == 1:
            total_option_list = [each_xx for each_menu in self.Menu_list for each_xx in option_dict[each_menu]]
            self.current_option_list = [each_xx for each_xx in option_dict[self.color_by_string_var.get()]]
        else:
            total_option_list = [f'{each_name}  {each_xx}' for each_name in select_item
                                 for each_menu in self.Menu_list for each_xx in option_dict[each_menu]]
            self.current_option_list = [f'{each_name}  {each_xx}' for each_name in select_item for each_xx in
                                        option_dict[self.color_by_string_var.get()]]
        self.color_dict = self.generate_color_dict(total_option_list)
        if use_default_color:
            self.color_dict["all_data"] = f"#{int(44):02x}{int(68):02x}{int(243):02x}"  # 设置默认颜色
        self.insert_xx_list_box(self.current_option_list, self.color_dict)
        self.current_select = self.current_option_list

    def color_by_string_var_event(self, select_item, x, y, z):
        """
        切换菜单，则更新当前筛选列表
        """
        if len(select_item) == 1:
            self.current_option_list = [each_xx for each_xx in self.option_dict[self.color_by_string_var.get()]]
        else:
            self.current_option_list = [f'{each_name}  {each_xx}' for each_name in select_item
                                        for each_xx in self.option_dict[self.color_by_string_var.get()]]
        self.insert_xx_list_box(self.current_option_list, self.color_dict)
        self.current_select = self.current_option_list



class ItemNameFrame:
    def __init__(self, master):
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)
        self.file_path_entry = ttk.Entry(master, width=49)
        self.file_path_entry.grid(row=0, column=0, pady=2,sticky="we")
        self.file_path_entry.delete(0, tk.END)
        # 测试项列表框

        self.item_name_list_box = tk.Listbox(master, selectmode="extended", width=50,
                                             height=15)
        self.item_name_list_box.grid(row=1, column=0, pady=2, sticky="wnes")
        # 测试项滚动条
        self.item_name_sb_ver = ttk.Scrollbar(master, orient="vertical")
        self.item_name_sb_ver.grid(row=1, column=1, pady=2, sticky="ens")
        self.item_name_sb_ver.configure(command=self.item_name_list_box.yview)  # 配置垂直滚动条
        self.item_name_list_box.config(yscrollcommand=self.item_name_sb_ver.set)  # xscrollcommand=sb_bottom.set

    def show_item_name(self, entry_value, item_name_list):
        self.file_path_entry.insert(0, entry_value)
        self.item_name_list_box.delete(0, tk.END)
        item_index = 0
        for each_item in item_name_list:
            self.item_name_list_box.insert(tk.END, '  ' + str(item_index) + ". " + each_item)
            item_index += 1

    def click_item_name(self, test_foms, old_select_item):
        item_name_list_box_select = self.item_name_list_box.curselection()
        current_select_item = [test_foms[each_item] for each_item in item_name_list_box_select] \
            if item_name_list_box_select != () else old_select_item
        return current_select_item


class InputDetailFrame:
    def __init__(self, master):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("my.Treeview", background="LightGrey", foreground="black")

        input_frame_button = tk.Frame(master)
        input_frame_button.pack(side="top", fill="both", anchor="w", pady=5)

        self.input_tree = ttk.Treeview(master, columns=[],
                                       show='headings', style="my.Treeview", height=11)
        self.input_tree.pack(expand=True, fill="both")

        sb_treex = ttk.Scrollbar(self.input_tree, orient="horizontal")
        sb_treex.pack(side="bottom", fill="x")  # grid 方法无法滚动，不知道为什么
        sb_treex.configure(command=self.input_tree.xview)  # 配置滚动条
        self.input_tree.config(xscrollcommand=sb_treex.set)  # xscrollcommand

        sb_treey = ttk.Scrollbar(self.input_tree, orient="vertical")
        sb_treey.pack(side="right", fill="y")
        sb_treey.configure(command=self.input_tree.yview)  # 配置滚动条
        self.input_tree.config(yscrollcommand=sb_treey.set)
        # 显示内容 并添加保存功能
        # -----------------   创建 生成GRR 数据 按钮--------------------
        tk.Label(input_frame_button, text="Test times:").grid(row=0, column=3)
        self.generate_GRR_times = tk.StringVar()
        times_entry = tk.Entry(input_frame_button, textvariable=self.generate_GRR_times, width=5)
        times_entry.grid(row=0, column=4)

        tk.Label(input_frame_button, text="Slot_name/index:").grid(row=0, column=5)
        self.generate_GRR_data_slot = tk.StringVar()
        slot_entry = tk.Entry(input_frame_button, textvariable=self.generate_GRR_data_slot, width=5)
        slot_entry.grid(row=0, column=6)

        generate_grr_data_button = ttk.Button(input_frame_button, text="Generate GRR data:", width=16)
        generate_grr_data_button.grid(row=0, column=1, padx=2)


class TitleEntryFrame:
    def __init__(self, master):
        row_title = 0
        column_title = 0
        # 创建limit...输入框
        row_title, column_title, self.minimum_entry = self.create_entry(row_title, column_title, master,
                                                                        "Minimum")
        row_title, column_title, self.vertical_line_entry = self.create_entry(row_title, column_title,
                                                                              master, "Vertical_line")
        row_title, column_title, self.lower_limit_entry = self.create_entry(row_title, column_title,
                                                                            master, "Lower limit")
        row_title, column_title, self.upper_limit_entry = self.create_entry(row_title, column_title,
                                                                            master, "Upper limit")
        # -------------------- 勾选框 --------------------
        # 画图模式
        self.draw_picture_mode = {"X axis is time": tk.IntVar(), "Fill bar": tk.IntVar(), "Is normed": tk.IntVar(),
                                  "Remove limit": tk.IntVar(), "Box image": tk.IntVar()}  # "remove_invalid": tk.IntVar(),
        for each_mode in self.draw_picture_mode.keys():
            tk.Checkbutton(master, text=each_mode,
                           variable=self.draw_picture_mode[each_mode]).grid(row=row_title, column=column_title,
                                                                            sticky="w")
            column_title += 1

    @staticmethod
    def create_entry(row_title, column_title, frame, label_name):
        tk.Label(frame, text=label_name).grid(row=row_title, column=column_title, sticky="w")
        column_title += 1
        entry = tk.Entry(frame, width=4)
        entry.grid(row=row_title, column=column_title, sticky="w")
        column_title += 1
        return row_title, column_title, entry


class TitleButtonFrame:
    def __init__(self,master):
        # 创建设置按钮
        self.button_name_dict = {"Load csv":None, "Save this image":None, "Save all item":None,
                                "Legend position":None, "Larger dot":None, "Smaller dot":None, "Change color":None,
                                "break_down":None, "run_GRR_report":None, "save all fail rate":None}
        row_title, column_title = 0, 0
        for each_button in self.button_name_dict:
            pad_x = 5
            if each_button == "run_GRR_report":
                foreground = "blue"
            else:
                foreground = "black"
            fun = ttk if platform.system()=="Windows" else tk
            self.button_name_dict[each_button] = fun.Button(master, text=each_button, foreground=foreground, width=12)
            self.button_name_dict[each_button].grid(row=row_title, column=column_title, padx=pad_x, pady=2, sticky="w")
            column_title += 1


class LoadProgressFram:
    def __init__(self, master):
        tk.Label(master, text="Load all data:").grid(row=0, column=0)
        style = ttk.Style()
        style.configure("TProgressbar", foreground="blue", background="blue")
        self.item_name_label = tk.Label(master, text="start")
        self.item_name_label.grid(row=0, column=1)
        self.progress_bar = ttk.Progressbar(master, maximum=100, value=0, style="TProgressbar")
        self.progress_bar.grid(row=0, column=2, sticky="w", padx=5)

        self.current_item_name_label = tk.Label(master, text="NA")
        self.current_item_name_label.grid(row=0, column=3, padx=5)
        self.current_item_progress_bar = ttk.Progressbar(master, maximum=100, value=0,
                                                         style="TProgressbar")
        self.current_item_progress_bar.grid(row=0, column=4, sticky="w", padx=5)


class DrawPictureGUI:
    def __init__(self):
        # self.root = tk.Toplevel(bg="white")  # 创建主界面
        self.root = tk.Tk()
        self.root.title("draw picture tool")  # 主界面名字
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        if platform.system() == "Windows":
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            print("缩放", scale_factor)
            MM_TO_IN = 1 / 25.4
            pxw = self.root.winfo_screenwidth()
            inw = self.root.winfo_screenmmwidth() * MM_TO_IN
            print("屏幕的实际尺寸是", self.root.winfo_screenmmwidth(), inw)
            self.root.tk.call('tk', 'scaling', scale_factor/100)
        self.root.geometry('%sx%s' % (int(self.screenwidth), int(self.screenheight)))

        # 创建框架
        self.root.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=2)
        # 测试项框架
        self.frame_item_list = tk.Frame(self.root)  # , bg="CornflowerBlue"
        self.frame_item_list.grid(row=0, column=0, padx=10, sticky="wnse")
        # SN/Station ID/config 列表框
        self.color_by_frame = tk.Frame(self.root)
        self.color_by_frame.grid(row=0, column=1, sticky='wnse')
        # 投产情况框架
        self.frame_input_detail = tk.Frame(self.root)
        self.frame_input_detail.grid(row=0, column=2, padx=2, sticky="wens")
        # 按钮框架
        self.frame_title_button = tk.Frame(self.root)
        self.frame_title_button.grid(row=1, column=0, columnspan=3, padx=10, sticky="we")
        self.frame_title_entry = tk.Frame(self.root)
        self.frame_title_entry.grid(row=2, column=0, columnspan=3, padx=10, sticky="we")
        # 画布框架
        self.frame_canvas = tk.Frame(self.root, padx=2)
        self.frame_canvas.grid(row=3, column=0, columnspan=3, sticky="wnse")
        # 底部进度条框架
        # self.frame_load_data_progress = tk.Frame(self.root)  # , bg="CornflowerBlue"
        # self.frame_load_data_progress.grid(row=4, column=0, columnspan=3, padx=10, sticky="we")
        # 框架对象
        self.item_name_frame_obj = ItemNameFrame(self.frame_item_list)
        self.color_by_list = ["all_data", "SerialNumber", "Special Build Description", "Station ID"]
        self.color_by_obj = ColorByMenuListBox(self.color_by_frame, self.color_by_list)
        self.color_by_obj.grid(row=0, column=0, sticky='wn')
        self.input_detail_frame_obj = InputDetailFrame(self.frame_input_detail)
        self.title_button_frame_obj = TitleButtonFrame(self.frame_title_button)
        self.title_entry_frame_obj = TitleEntryFrame(self.frame_title_entry)
        # self.load_progress_frame_obj = LoadProgressFram(self.frame_load_data_progress)
        self.root.protocol('WM_DELETE_WINDOW', self.close_gui)

    def close_gui(self, event=None):
        print("程序关闭")
        self.root.destroy()
