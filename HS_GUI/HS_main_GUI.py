# 自带模块
import os
import sys
import traceback
from time import sleep
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import platform
import threading
import re
import time
import datetime
import webbrowser
from multiprocessing import Queue
import shutil
if platform.system() == "Windows":
    import ctypes
    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    #print("缩放系数是", ScaleFactor)
    # import pathos
    # from pathos.multiprocessing import ProcessingPool

# 第三方库
from PIL import Image, ImageTk

from HS_tool_son_GUI import HS_tool_setting_app, HS_tool_tool, Contact_listbox
from user_info_GUI import User_info_app
from haimeng_tk import color_change, change_photo
from HS_universal.haimeng_time import changelocaltimeToSqldatetime
from HS_universal.HS_directory import HS_directory


class HS_tool_GUI:
    def __init__(self, root):
        self.HS_directory = HS_directory()
        self.root = root
        self.root.resizable(1, 1)
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        # print("创建主界面")
        self.init_GUI()
        if platform.system() == "Windows":
            self.root.tk.call('tk', 'scaling', 2)
            self.root_width = int(self.screenwidth * 0.65)
            self.root_height = int(self.screenheight * 0.5)
        else:
            # self.root.tk.call('tk', 'scaling', 2560/1440)
            self.root_width = int(self.screenwidth * 0.7)
            self.root_height = int(self.screenheight * 0.53)
        self.root.geometry('%sx%s' % (self.root_width, self.root_height))
        self.root.geometry('+%s+%s' % (int((self.screenwidth - self.root_width) / 2),
                                       int((self.screenheight - self.root_height) / 2)))  # 在屏幕中间开启窗口
        self.HS_tool_GUI_frame.pack(fill="both",expand=True)

    def init_GUI_parameter(self):
        # 属性参数
        self.root_column0_bg = color_change(49, 49, 49) # 第一列背景色
        self.root_column0_fg = color_change(0, 255, 255)  # 第一列字体的前景色
        if platform.system()=="Windows":
            self.my_name_ft = tkFont.Font(family='黑体', size=16)  # 第一列我的名字字体
            self.my_sign_font = tkFont.Font(family='黑体', size=11)  # 第一列我的签名字体
            self.reflesh_friend_icon_font = tkFont.Font(family='微软雅黑', size=14)
            self.entry_input_font = tkFont.Font(family='微软雅黑', size=12)
            self.setting_font = tkFont.Font(family='微软雅黑', size=12)
            self.send_file_button_ft = tkFont.Font(family='微软雅黑', size=12)
        else:
            self.my_name_ft = tkFont.Font(family='黑体', size=16)  # 第一列我的名字字体
            self.my_sign_font = tkFont.Font(family='黑体', size=12)  # 第一列我的签名字体
            self.reflesh_friend_icon_font = tkFont.Font(family='微软雅黑', size=12)
            self.entry_input_font = tkFont.Font(family='微软雅黑', size=14)
            self.setting_font = tkFont.Font(family='微软雅黑', size=14)
            self.send_file_button_ft = tkFont.Font(family='微软雅黑', size=12)
        self.avatar_width = int(self.screenwidth * 0.03) # 好友头像宽度
        self.contact_listbox_width = int(self.screenwidth * 0.16) # 好友列表初始宽度
        self.input_ip_frame_width = int(self.screenwidth * 0.15)
        if platform.system()=="Windows":
            self.input_ip_pady = 10
        else:
            self.input_ip_pady = 10
        self.my_sign_color = color_change(230, 230, 230)
        self.input_ip_fg = color_change(30,30,30)
        self.input_ip_bg = color_change(200, 200, 200)
        self.chat_window_bg = color_change(245, 245, 245)
        self.chat_name_bg = color_change(245, 245, 245)

        self.ttk_style = ttk.Style()
        self.ttk_style.configure("TCombobox",background=self.input_ip_bg,foreground=self.input_ip_fg)

    def init_GUI(self):
        self.init_GUI_parameter()
        self.HS_tool_GUI_frame = tk.Frame(self.root)
        self.HS_tool_GUI_frame.rowconfigure(0, weight=1)
        self.HS_tool_GUI_frame.columnconfigure(1, weight=1)
        # 第一列
        self.root_column0 = tk.Frame(self.HS_tool_GUI_frame, bg=self.root_column0_bg)
        self.root_column0.grid(row=0, column=0, sticky="nswe")
        self.place_root_column0()
        # 第二列（包含两列）
        self.root_painewindow = tk.PanedWindow(self.HS_tool_GUI_frame)
        self.root_painewindow.grid(row=0, column=1, sticky="nswe")
        self.root_column1 = tk.Frame(self.root_painewindow)
        self.root_column2 = tk.Frame(self.root_painewindow)
        self.place_root_column1()
        self.place_root_column2()
        self.root_painewindow.add(self.root_column1)
        self.root_painewindow.add(self.root_column2)

    def show_HS_tool_GUI(self):
        self.root.title("HS")
        # for windows
        if platform.system() == "Windows":
            self.root.tk.call('tk', 'scaling', 2)
            self.root_width = int(self.screenwidth * 0.65)
            self.root_height = int(self.screenheight * 0.5)
        else:
            self.root_width = int(self.screenwidth * 0.7)
            self.root_height = int(self.screenheight * 0.53)
        self.root.geometry('%sx%s' % (self.root_width, self.root_height))
        self.root.geometry('+%s+%s' % (int((self.screenwidth - self.root_width) / 2),
                                       int((self.screenheight - self.root_height) / 2)))  # 在屏幕中间开启窗口
        self.HS_tool_GUI_frame.pack(fill="both",expand=True)

    # ===============  点击可拖动界面 ================
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x  # 鼠标移动的距离
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax  # 窗口的左上角坐标 加鼠标移动的距离
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))


    def place_root_column0(self):
        self.root_column0.bind("<ButtonPress-1>", self.StartMove)
        self.root_column0.bind("<ButtonRelease-1>", self.StopMove)
        self.root_column0.bind("<B1-Motion>", self.OnMotion)
        # 获取头像和签名, 优先从服务器获取，服务器不在线或者没有再从本地获取，服务器和本地都有，如果两者不一样，则更新
        # 初始化用户头像，签名
        # 初始化tool 图标
        self.root_column0.columnconfigure(1, weight=1)
        self.default_avatar_path = os.path.join(self.HS_directory.tool_picture_dir, "login.png")
        self.default_avatar = change_photo(
            self.default_avatar_path, int(self.screenwidth * 0.03), is_zoomout=True, is_square=True)[0]
        self.my_photo_label = tk.Label(self.root_column0, image=self.default_avatar, cursor='hand2')
        self.my_photo_label.grid(row=0,rowspan=2, column=0, pady=5, sticky="nsw")

        self.my_name_label = tk.Label(self.root_column0, text="无名", font=self.my_name_ft,
                                      fg="white", bg=self.root_column0_bg, cursor='hand2')
        self.my_name_label.grid(row=0, column=1, pady=5, sticky="w")

        self.my_sign_label = tk.Label(self.root_column0, text="请让我独享经验",
                            fg=self.my_sign_color, font=self.my_sign_font, bg=self.root_column0_bg, cursor='hand2')
        self.my_sign_label.grid(row=1, column=1,sticky="w")
        self.my_sign_label2 = tk.Label(self.root_column0, text="",
                                       fg=self.my_sign_color,
                                       font=self.my_sign_font, bg=self.root_column0_bg)
        self.my_sign_label2.grid(row=3, column=0, columnspan=2, sticky="w")

        self.tool_frame = tk.Frame(self.root_column0, bg=self.root_column0_bg)
        self.tool_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="wns")

        self.root_column0.rowconfigure(5, weight=1)
        self.setting_label = tk.Label(self.root_column0, text="设置", font=self.setting_font,
                                      bg=self.root_column0_bg, fg="white", cursor='hand2')
        self.setting_label.grid(row=6, column=0, sticky="ws")
        self.help_label = tk.Label(self.root_column0, text="帮助", font=self.setting_font,
                                      bg=self.root_column0_bg, fg="white", cursor='hand2')
        self.help_label.bind("<ButtonPress-1>", self.click_help)
        self.help_label.grid(row=6, column=1, sticky="ws")


    def click_help(self,event=None):
        if platform.system()=='Darwin':
            os.system(f"open '{self.HS_directory.help_document}'")

    def click_input_ip(self, event):
        if self.input_ip.get() == "搜索账号/ip添加联系人":
            self.input_ip.delete(0, tk.END)
            self.ttk_style.configure("TCombobox", background=self.input_ip_bg,foreground=self.input_ip_fg)

    def delete_input_ip(self, event):
        pass
        # self.back_to_chat()

    def focus_out_input_ip(self, event):
        if self.input_ip.get() == "":
            # self.input_ip.configure(fg="gray")
            self.ttk_style.configure("TCombobox",background=self.input_ip_bg,foreground=self.input_ip_fg)
            self.input_ip.insert(0, "搜索账号/ip添加联系人")

    def in_reflesh_friend_label(self,event):
        self.reflesh_friend_label["bg"] = color_change(120, 248, 90)

    def out_reflesh_friend_label(self,event):
        self.reflesh_friend_label["bg"] = "White"

    def place_root_column1(self):
        # 从服务器获取联系人列表（头像，昵称，签名），按在线状态和时间排序，只显示前100个联系人，每个联系人加载100条记录
        # 每次聊天，需要向服务器刷新好友时间和本地保存聊天记录
        # 服务器不在线则加载本地聊天记录，聊天记录不保存到服务器（开线程加载）
        # 每次新增聊天，则将新增的联系人写入好友数据库（先检查好友数据库有没有该好友）
        if platform.system()=="Windows":
            relief = "groove"
        else:
            relief = None
        self.input_ip_frame = tk.Frame(self.root_column1, width=self.input_ip_frame_width,bg=self.chat_name_bg,
                                       relief=relief, borderwidth=0.5)
        self.input_ip_frame.grid(row=0, column=0,columnspan=2, sticky="nsew")

        self.reflesh_friend_label = tk.Label(self.input_ip_frame,text="↻",font=self.reflesh_friend_icon_font, cursor='hand2')
        self.reflesh_friend_label.grid(row=0, column=0)
        self.reflesh_friend_label.bind("<Enter>",self.in_reflesh_friend_label)
        self.reflesh_friend_label.bind("<Leave>",self.out_reflesh_friend_label)

        self.input_ip_frame.columnconfigure(1, weight=1)
        self.input_ip = ttk.Combobox(master=self.input_ip_frame,style="TCombobox")
        self.input_ip.grid(row=0, column=1, padx=5, pady=self.input_ip_pady,sticky="nsew")
        self.ttk_style.configure("TCombobox", background=self.input_ip_bg,foreground=self.input_ip_fg)
        self.input_ip.insert(0, "搜索账号/ip添加联系人")
        self.input_ip.bind("<Button-1>", self.click_input_ip)
        self.input_ip.bind("<KeyRelease-BackSpace>", self.delete_input_ip)
        self.input_ip.bind("<FocusOut>", self.focus_out_input_ip)

    def root_tool_chat_frame_place(self):
        '''
        初始化聊天窗名字框架，聊天框架
        初始化联系人列表
        '''
        self.root_tool_chat_frame.columnconfigure(0, weight=1)
        self.chat_name_frame = tk.Frame(self.root_tool_chat_frame,bg=self.chat_name_bg)
        self.chat_name_frame.grid(row=0, column=0, sticky="ewns")

        self.root_tool_chat_frame.rowconfigure(1, weight=1)
        self.chat_window_frame = tk.Frame(self.root_tool_chat_frame, relief="groove", borderwidth=0.5)
        self.chat_window_frame.grid(row=1, column=0, sticky="ewns")

        self.root_column1.rowconfigure(1, weight=1)
        self.root_column1.columnconfigure(0, weight=1)
        self.contact_listbox = Contact_listbox(self.root_column1, self.chat_name_frame,
                                               self.chat_window_frame, width=self.contact_listbox_width)
        self.contact_listbox.grid(row=1, column=0, sticky="ewns")

    def entry_message_change_height(self, event):
        '''
        输入框换行时增加它的高度
        :param event: 每当按下Ctrol+enter触发
        :return: None
        '''
        self.entry_control_return_flag = True
        # if self.entry_message_height < 10:
        #     self.entry_message_height += 1
        #     self.entry_message.configure(height=self.entry_message_height)
        self.entry_message.see(tk.END)

    def entry_message_delete_content(self, event):
        '''
        输入框删除内容时减少它的高度
        '''
        current_content = self.entry_message.get("1.0", tk.END)
        enter_count = current_content.count("\n")
        if self.entry_message_height > 3 and enter_count < 15:
            self.entry_message_height = enter_count
            self.entry_message.configure(height=self.entry_message_height)
        self.entry_message.see(tk.END)

    def remove_start_enter(self, string):
        data = string
        data_re = re.search(" \n", data)
        while data_re != None:
            data = data[1:]
            data_re = re.search(" \n", data)
            if data == "":
                return ""
        return data

    def remove_end_enter(self, string):
        data = string
        data_re = re.search("\n$", data)
        while data_re != None:
            data = data[:-1]
            data_re = re.search("\n$", data)
            if data == "":
                return ""
        return data

    def root_tool_frame_entry_message_place(self):
        '''
        创建输入框及其绑定的函数/操作
        '''
        self.root_tool_entry_message_frame.rowconfigure(1, weight=1)
        self.entry_control_return_flag = False

        self.root_tool_entry_message_frame.columnconfigure(3, weight=1)
        self.entry_message_height = 1
        self.entry_message = tk.Text(self.root_tool_entry_message_frame,
                                     highlightthickness=0,
                                     borderwidth=0,
                                     font=self.entry_input_font,
                                     height=3)
        self.entry_message.grid(row=1, column=0,columnspan=4,padx=10, pady=10,sticky="wens")
        self.entry_message.bind("<Control-KeyPress-Return>", self.entry_message_change_height)
        # todo 绑定粘贴操作
        self.file_button = tk.Label(self.root_tool_entry_message_frame, text="文件",
                                    font=self.send_file_button_ft,bg="orange",fg="white", cursor='hand2')
        self.file_button.grid(row=0, column=0, padx=10, sticky="w")
        self.directory_button = tk.Label(self.root_tool_entry_message_frame, text="目录",
                                         font=self.send_file_button_ft,bg="orange",fg="white", cursor='hand2')
        self.directory_button.grid(row=0, column=1, padx=10, sticky="w")

    def place_root_column2(self):
        # 聊天窗口框
        self.root_column2.rowconfigure(0, weight=1)  # root第0行权重1, 使得self.root_tool_frame_text纵向填充
        self.root_column2.columnconfigure(0, weight=1)  # 权重越大，占的空间越小，总权重是每一列配置权重的和

        self.root_tool_chat_frame = tk.Frame(self.root_column2, bg=self.chat_window_bg)
        self.root_tool_chat_frame.grid(row=0, column=0, sticky="nswe")
        self.root_tool_chat_frame_place()
        # 聊天输入框
        self.root_tool_entry_message_frame = tk.Frame(self.root_column2,bg="white", relief="groove", borderwidth=0.7)
        self.root_tool_entry_message_frame.grid(row=1, column=0, sticky="wens")
        self.root_tool_frame_entry_message_place()


class HS_tool_tool_GUI(HS_tool_GUI):
    def __init__(self,root,account, **kwargs):
        """
        添加工具按钮
        """
        super().__init__(root)
        self.HS_tool_setting_app = HS_tool_setting_app(account)
        self.HS_tool_tool_obj = HS_tool_tool(self.HS_tool_setting_app)
        self.tool_frame_place()
        self.setting_label.bind("<ButtonPress-1>", self.click_setting)

    def click_setting(self,event=None):
        self.HS_tool_setting_app.create_setting_GUI()

    def create_tool_button(self, index):
        tool_path = os.path.join(self.HS_directory.tool_picture_dir,self.tool_list[index]["image_path"])
        self.tool_list[index]["image"] = change_photo(tool_path,int(self.screenwidth * 0.02),is_zoomout=True,is_square=True)[0]

        # self.tool_image_list.append(image) # 如果不保存图像到self，tkinter的机制无法显示图片
        button = tk.Button(self.tool_frame, image=self.tool_list[index]["image"],
                           command=self.tool_list[index]["function"], cursor='hand2')
        button.grid(row=index, column=0, sticky="w")

        label = tk.Label(self.tool_frame, text=self.tool_list[index]["name"], fg=self.root_column0_fg,
                         bg=self.root_column0_bg, cursor='hand2')
        label.grid(row=index, column=1, sticky="w")
        label.bind("<ButtonPress-1>", lambda event: self.tool_list[index]["function"]())

    def tool_frame_place(self):
        # print("放置工具")
        self.tool_list = [
            {"image_path": "daily_report.png", "image": None, "name": "Daily Report","function": self.HS_tool_tool_obj.daily_report_tool},
            {"image_path": "opp_grr.png", "image": None, "name": "OPP GRR", "function": self.HS_tool_tool_obj.draw_test_item_picture},
            # {"image_path": "rush_compare.png", "image": None, "name": "Compare Rush", "function": self.HS_tool_tool_obj.compare_rush},
            {"image_path": "overlay_foms.png", "image": None, "name": "overlayFOM 对比",
             "function": self.HS_tool_tool_obj.overlay_FOMs_tool},
            {"image_path": "find_records.png", "image": None, "name": "Find Records.csv",
             "function": self.HS_tool_tool_obj.find_records_csv},
            {"image_path": "BOM_audit.png", "image": None, "name": "BOM audit",
             "function": self.HS_tool_tool_obj.BOM_audit_},
            {"image_path": "miao_biao.png", "image": None, "name": "秒表", "function": self.HS_tool_tool_obj.fun_timer},
            {"image_path": "DUT.png", "image": None, "name": "机台通信", "function": self.HS_tool_tool_obj.dut_communication},
            {"image_path": "web.png", "image": None, "name": "我的网站", "function": self.open_web_version}

            # {"image_path": "send_file.PNG", "image": None, "name": "文件传输","function": self.HS_tool_tool_obj.send_file}
        ]
        i = 0
        for each_tool_button in self.tool_list:
            self.create_tool_button(i)
            i += 1

    def detect_static_file(self):
        home_path = self.HS_directory.tool_home_dir
        have_static = False
        HS_server_django_symple_path = ""
        for current_path, dirs, files in os.walk(home_path):
            # print(current_path, dirs, files)
            if "HS_server_django_symple" == os.path.basename(current_path):
                print("找到路径", current_path, os.listdir(current_path))
                HS_server_django_symple_path = current_path
                if "static" in os.listdir(current_path):
                    have_static = True
                    return have_static, HS_server_django_symple_path
        return have_static, HS_server_django_symple_path

    def cp_static(self, HS_server_django_symple_path):
        # 复制资源包到django项目路径
        static_path = ""
        directory = tkfile.askdirectory(message="选择资源包或者旧版app所在文件夹")
        if directory:
            if os.path.basename(directory) == "static":
                static_path = directory
            else:
                for current_path, dirs, files in os.walk(directory):
                    if "static" == os.path.basename(current_path) and "HS_server" in os.listdir(current_path):
                        static_path = current_path
            if static_path:
                print("找到资源包", static_path)
                # todo 把找到的资源包移动/复制到HS_server_django_symple_path下面
                # shutil.copytree(static_path, os.path.jion(HS_server_django_symple_path, "static"))
                shutil.move(static_path, HS_server_django_symple_path)
                tk.messagebox.showinfo("Hi", "资源包加载完成，请重启")
            else:
                tk.messagebox.showinfo("Hi", "你选择的路径下找不到资源包")


    def open_web_version(self):
        have_static, HS_server_django_symple_path = self.detect_static_file()
        if have_static:
            if platform.system() == "Windows":
                webbrowser.open("http://192.168.0.103:7788/HS_server")
            else:
                webbrowser.open("http://127.0.0.1:7799/HS_server")
        else:
            self.cp_static(HS_server_django_symple_path)


event_dict = dict()
def add_event2dict(event_name):
    '''
    将事件名和对应函数名添加到字典的装饰器
    '''
    def set_fun(fun):
        event_dict[event_name] = fun  # 这一步只有装饰的时候才会被调用
        def call_fun(*args, **kwargs):
            return fun(*args, **kwargs)
        return call_fun
    return set_fun

class HS_tool_app(HS_tool_tool_GUI):
    def __init__(self,root, account, **kwargs):
        '''
        处理事件
        1. 获取联系人（包括自己）信息
        2. 点击显示联系人信息
        3. 修改联系人（包括自己）的信息
        4. 增删查联系人
        5. 发送、接收消息
        6、 发送、接收文件
        '''
        super().__init__(root, account, **kwargs)
        self.account = account
        self.my_photo_path = os.path.join(self.HS_directory.tool_picture_dir, "login.png")
        self.my_info_dict = {}
        self.friend_dict = {}
        self.cookie = ""
        self.my_info_dict = self.HS_directory.read_user_info_file(account)
        # 先从本地加载个人信息和好友列表
        if "name" in self.my_info_dict and "sign" in self.my_info_dict and "photo" in self.my_info_dict:
            self.update_my_info(self.my_info_dict["name"], self.my_info_dict["sign"], self.my_info_dict["photo"], is_from_local=True)
        if "friend_dict" in self.my_info_dict:
            self.friend_dict = self.my_info_dict["friend_dict"]
            for index, each_account in enumerate(self.friend_dict):
                self.update_friend(index, each_account)
        if "q_recv" in kwargs and "q_sent" in kwargs and "cookie" in kwargs:
            self.q_sent = kwargs["q_sent"]
            self.q_recv = kwargs["q_recv"]
            self.cookie = kwargs["cookie"]

            self.handle_event_threading = threading.Thread(target=self.get_q)
            self.handle_event_threading.daemon = True
            self.handle_event_threading.start()
            self.bind_event()
            update_info_thread = threading.Thread(target=self.update_info)
            update_info_thread.daemon = True
            update_info_thread.start()
            self.update_time_interval = 60

    def reflesh_info(self, event=None):
        # print("获取信息事件")
        self.get_my_info()
        self.get_friend_info()
        self.get_message()

    def update_info(self):
        while True:
            # print("刷新信息")
            self.reflesh_info()
            # time.sleep(self.update_time_interval)
            time.sleep(300)

    def root_activate(self, event):
        # print("组件被唤醒")
        self.update_time_interval = 10

    def root_deactivate(self, event):
        # print("组件进入休眠")
        self.update_time_interval = 300

    def bind_event(self):
        self.my_photo_label.bind("<ButtonPress-1>", self.click_my_photo)  # 点击我的头像时
        self.my_sign_label.bind("<ButtonPress-1>", self.click_my_photo)  # 点击我的签名时
        self.reflesh_friend_label.bind("<ButtonPress-1>", self.reflesh_info)  # 点击刷新按钮
        self.input_ip.bind("<<ComboboxSelected>>", self.add_new_friend_from_search)  # 选择搜索用户结果时
        self.input_ip.bind("<KeyPress-Return>", self.search_friend)  # 搜索框按下回车时
        self.entry_message.bind("<KeyRelease-Return>", self.send_message)  # 发送消息
        send_file_CMD = lambda event: self.send_file(event=event)
        self.file_button.bind("<ButtonPress-1>", send_file_CMD)  # 发送文件
        self.directory_button.bind("<ButtonPress-1>", self.send_directory)  # 发送文件夹
        self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)  # 关闭窗口
        self.HS_tool_GUI_frame.bind('<Activate>', self.root_activate)
        self.HS_tool_GUI_frame.bind('<Deactivate>', self.root_deactivate)

    def close_GUI(self):
        self.root.destroy()



# ++++++++++++++++++++++++++++++++++++++获取我的信息++++++++++++++++++++++++++++++++
    def update_my_info(self, name, sign, photo, is_from_local=False):
        # ----------更新名字---------
        if name:
            self.my_name_label["text"] = name
        # ----------更新签名---------
        if sign:
            if len(sign) > 7:  # 签名过长分两行显示
                self.my_sign_label["text"] = sign[:7]
                end_num = 20 if len(sign) > 20 else len(sign)
                self.my_sign_label2["text"] = sign[7:end_num]
            else:
                self.my_sign_label["text"] = sign
                self.my_sign_label2["text"] = ""
        # ----------更新头像---------
        if photo:
            photo_path = os.path.join(self.HS_directory.user_avartar_dir, photo)
            if not os.path.exists(photo_path):
                # todo 头像不存在，申请下载
                if not is_from_local:
                    self.get_avatar(self.account)
            else:
                self.my_photo_path = photo_path
                self.my_photo = \
                    change_photo(photo_path, self.avatar_width, is_zoomout=True, is_square=True)[0]
                self.my_photo_label["image"] = self.my_photo

    @add_event2dict("get_avatar")
    def get_avatar_result(self, header_dict, body):
        # print("GUI收到获取头像结果")
        if "file_name" in header_dict and body=="success":
            self.reflesh_info()

    def get_avatar(self, account):
        save_path = self.HS_directory.user_avartar_dir
        if self.cookie:
            self.sent_event({"event": "get_avatar", "cookie": self.cookie, "target_account": account,
                         "content_type": "text", "save_path": save_path}, "")

    def get_my_info(self):
        # print("获取我的信息")
        self.sent_event({"event": "get_my_info", "cookie": self.cookie, "content_type": "text"}, "")

    @add_event2dict("get_my_info")
    def get_my_info_result(self, header_dict, body):
        # 返回顺序id,account,password,name,ip,port,is_online,photo,sign,birthday,gender,address,phone,mail,
        # is_delete,cookie,fd_file,connect_time,internal_port
        # print("返回了我的信息", header_dict)
        if body and isinstance(body, tuple):
            my_info_list = list(body[0])
            key_list = ["name", "sign", "photo", "birthday", "gender", "address", "phone", "mail"]
            for i, key in enumerate(key_list):
                self.my_info_dict[key] = my_info_list[i]
            self.update_my_info(self.my_info_dict["name"], self.my_info_dict["sign"], self.my_info_dict["photo"])
            self.HS_directory.write_user_info_file(self.account, self.my_info_dict)


# +++++++++++++++++++++++++++++++++++++++获取我的好友列表++++++++++++++++++++++++++++
    def replace_info(self,account, parametor_list, value_list):
        """
        当查不到账户相关信息时， 将查不到的信息设为默认值
        parameter_list = ["image_name", "name", "sign", "contact_time", "message", "is_online"] 信息名
        value_list 查到的信息值
        result_list 替换默认值后的信息值
        """
        result_list = []
        i = 0
        for each_key in parametor_list:
            if each_key == "image_name":
                if value_list[i] == "":
                    result = self.HS_directory.default_avatar
                else:
                    result = os.path.join(self.HS_directory.user_avartar_dir, value_list[i])
                    # print("该用户头像是", result)
                    if not os.path.exists(result):  # todo 如果好友头像不存在，需要申请下载
                        result = self.HS_directory.default_avatar
                        # print("本地找不到该用户头像", result)
                        self.get_avatar(account)
            elif each_key=="name":
                result = account if value_list[i] == "" else value_list[i]
            elif each_key=="sign":
                result = "" if value_list[i] == "" else value_list[i]
            elif each_key =="contact_time":
                if "str" in str(type(value_list[i])):
                    # print("收到消息的时间是", value_list[i])
                    result = value_list[i].split(' ')[-1]
                elif value_list[i] is None:
                    result = changelocaltimeToSqldatetime().split(' ')[-1]
                else:
                    result = value_list[i].strftime("%Y-%m-%d %H:%M:%S").split(' ')[-1]
            elif each_key == "message":
                result = value_list[i]
            elif each_key == "is_online":
                result = "在线" if value_list[i]==b'\x01' else "离线"
            else:
                result = ""
            result_list.append(result)
            i += 1
        return result_list

    # *********************************** 显示用户信息 *****************************
    @add_event2dict("modify_my_info")
    def modify_my_info_result(self, header_dict, body):
        if body == "success":
            # print("修改我的信息成功")
            self.reflesh_info()

    @add_event2dict("modify_friend_info")
    def modify_friend_info_result(self, header_dict, body):
        if body == "success":
            # print("修改好友信息成功")
            self.reflesh_info()

    @add_event2dict("change_my_avatar")
    def change_my_avatar_result(self, header_dict, body):
        # print("修改头像结果", header_dict, body)
        if body == "success":
            # print("修改我的头像成功")
            self.reflesh_info()
            try:
                self.user_info_GUI.change_user_photo_success()
            except:
                pass

    def show_account_GUI(self, account):
        """
        显示 用户信息 界面
        """
        # kwargs["photo"], kwargs["name"], kwargs["nickname"],
        #                                 kwargs["sign"], kwargs["birthday"], kwargs["gender"],
        #                                 kwargs["address"], kwargs["phone"], kwargs["mail"],
        #                                 ""
        if account==self.account and account not in self.friend_dict:
            user_info_dict = self.my_info_dict
            user_info_dict["nickname"] = ""
        else:
            user_info_dict = self.friend_dict[account]
        # print("用户信息++++++++++++++++++++", user_info_dict)
        if "cookie" not in user_info_dict:
            user_info_dict["cookie"] = self.cookie
        self.user_info_GUI = User_info_app(owner_account=self.account, sent_event_fun=self.sent_event, **user_info_dict)
        self.root.mainloop()

    def click_my_photo(self, event):
        self.show_account_GUI(self.account)


    # 插入好友
    def insert_friend(self, index, account, **kwargs):
        """
        有可能给的参数kwargs不全，则设为默认参数， 插入函数需要的参数如下
        contact_listbox.insert(self, index, image_path, name, sign, time_str, message, status,
                        account, chat_name_frame, chat_window_frame):
        插入后重新绑定点击头像事件，点击删除按钮事件
        """
        parametor_list = ["image_name", "name", "sign", "contact_time", "message", "is_online"]
        result_list = []
        for each_para in parametor_list:
            if each_para in kwargs:
                result_list.append(kwargs[each_para])
            else:
                result_list.append("")
        result_list = self.replace_info(account, parametor_list, result_list)
        self.contact_listbox.insert(index, *result_list, account)
        item = self.contact_listbox.item_dict[account]["item"]
        item.tk_image_label.unbind("<ButtonPress-1>")
        # todo 绑定点击就显示好友信息
        show_account_GUI_CMD = lambda event: self.show_account_GUI(account)
        item.tk_image_label.bind("<ButtonPress-1>", show_account_GUI_CMD)
        delete_friend_CMD = lambda event: self.delete_friend(account, item)
        item.delete_mark.bind("<ButtonPress-1>", delete_friend_CMD)

    def update_friend(self, index, account, contact_time=None):
        """
        1. 插入联系人需要上锁，防止其他地方如接收到新消息也插入同一个联系人导致重复
        2. 如果账户不在好友列表，则在联系人框添加该账户， 否则更新该账户状态即可
        3. 如果本地没有好友的头像，申请下载？
        """
        account, name, sign, photo, is_online, nickname, time = self.friend_dict[account]["account"], \
                                                                self.friend_dict[account]["name"], \
                                                                self.friend_dict[account]["sign"], \
                                                                self.friend_dict[account]["photo"],\
                                                                self.friend_dict[account]["is_online"],\
                                                                self.friend_dict[account]["nickname"],\
                                                                self.friend_dict[account]["time"]
        if contact_time is None:
            if time:
                contact_time = time
            else:
                contact_time = "--- ---"
        # print("该联系人时间是", contact_time)
        # print(account, name, sign, photo, is_online,
         # birthday, gender, address, phone, mail, nickname, contact_time)
        if nickname != "":
            name = nickname
        if account not in self.contact_listbox.item_dict:
            # print("插入", name, sign, photo)
            self.insert_friend(index, account, name=name, sign=sign, image_name=photo,
                               contact_time=contact_time, isonline="", is_online=is_online)
        else:
            # print("开始更新好友信息", name)
            parametor_list = ["image_name", "name", "sign", "contact_time", "message", "is_online"]
            value_list = [photo, name, sign, contact_time, "", is_online]
            result_list = self.replace_info(account, parametor_list, value_list)  # 替换列表中的空值为默认值
            self.contact_listbox.update_user_info(account, image_path=result_list[0], name=result_list[1],
                                                  sign=result_list[2], contact_time=result_list[3], status=result_list[5])
            # print("更新完成",self.contact_listbox.item_dict[account])
            # if is_online:
            #     self.contact_listbox.change_item_index(self.contact_listbox.item_dict[account]["item"].index, 0)

    def get_friend_info(self):
        self.sent_event({"event": "get_friend_info", "cookie": self.cookie, "content_type": "text"},  "")

    @add_event2dict("get_friend_info")
    def get_friend_info_result(self, header_dict, body):
        # print("收到用户信息结果", threading.current_thread(), header_dict, body)
        # if 'tuple' in str(type(body)) and body:
        self.friend_dict = {}
        if body and isinstance(body, tuple):
            for index, each_friend in enumerate(body):
                [account, name, sign, photo, is_online,
                            birthday, gender, address, phone, mail, ip, nickname, time] = list(each_friend)
                # self.friend_dict[account] = list(each_friend)
                self.friend_dict[account] = {"account": account,
                    "name": name, "sign":sign, "photo":photo, "is_online":is_online, "birthday":birthday,
                    "gender":gender, "address":address, "phone":phone, "mail":mail, "ip":ip,
                    "nickname":nickname, "time":time
                }
                # print(f"名字：{name}，签名:{sign}")
                self.update_friend(index, account)
            # print("更新好友信息到本地", self.friend_dict)
        self.HS_directory.write_user_info_file(self.account, {"friend_dict": self.friend_dict})


# +++++++++++++++++++++++++++++++++++++++删除好友++++++++++++++++++++++++++++
    def delete_friend(self, account, item):
        self.sent_event(
            {"event": "delete_friend", "cookie": self.cookie, "target_account": account, "content_type": "text"}, "")


    @add_event2dict("delete_friend")
    def delete_friend_result(self, header_dict, body):
        if body == "success":
            # print("删除好友成功")
            account = header_dict["target_account"]
            item = self.contact_listbox.item_dict[account]["item"]
            self.contact_listbox.delete_item(account, item)
            # print("我的好友列表", self.friend_dict)
            if account in self.friend_dict:
                self.friend_dict.pop(account)
                self.HS_directory.write_user_info_file(self.account, {"friend_dict": self.friend_dict})
        else:
            tkmessage.showerror("Hi", "服务器未响应，请稍后再试")

# +++++++++++++++++++++++++++++++++++++++添加好友++++++++++++++++++++++++++++
    @add_event2dict("add_new_friend")
    def add_new_friend_result(self, header_dict, body):
        # print("添加好友成功")
        if body == "success":
            # self.reflesh_info()
            new_add_friend = eval(header_dict["result"])[0]
            # print("添加好友成功", new_add_friend)
            [account, name, sign, photo, is_online,
             birthday, gender, address, phone, mail, ip, nickname, time] = list(new_add_friend)
            self.friend_dict[account] = {"account": account,
                                         "name": name, "sign": sign, "photo": photo, "is_online": is_online,
                                         "birthday": birthday, "gender": gender, "address": address, "phone": phone,
                                         "mail": mail, "ip": ip, "nickname": nickname, "time": time
                                         }
            self.HS_directory.write_user_info_file(self.account, {"friend_dict": self.friend_dict})
            self.update_friend(0, header_dict["target_account"])
        else:
            tkmessage.showerror("Hi", "服务器未响应，请稍后再试")

    def add_new_friend(self, from_account, recv_time=""):
        """
        添加新的好友，
        """
        if recv_time == "":
            recv_time = changelocaltimeToSqldatetime()
        if from_account not in self.friend_dict:
            # print("正在添加好友", from_account)
            self.friend_dict[from_account] = {"account": from_account,
                    "name": from_account, "sign":"", "photo":"", "is_online":b'\x00', "birthday":"",
                    "gender":"", "address":"", "phone":"", "mail":"", "ip":"", "nickname":"", "time":recv_time
                }
            self.update_friend(0, from_account)
            # self.HS_directory.write_user_info_file(self.account, {"friend_dict": self.friend_dict})
        self.sent_event(
            {"event": "add_new_friend", "cookie": self.cookie, "target_account": from_account, "content_type": "text"},
            "")


# +++++++++++++++++++++++++++++++++++++++搜索好友++++++++++++++++++++++++++++
    def add_new_friend_from_search(self, event):
        """
        当用户点击搜索结果列表时， 添加对应的选项到好友列表
        """
        # select_index = self.input_ip.current()
        account = self.input_ip.get()
        if account not in self.contact_listbox.item_dict:
            self.add_new_friend(account)

    def search_friend(self, event):
        """
        发送服务器开始检索
        将检索内容添加到combobox
        判定用户选择的选项，添加联系人
        """
        input_char = self.input_ip.get()
        if input_char != "":  # 防止搜索到全部的好友
            self.sent_event(
                {"event": "search_friend", "cookie": self.cookie, "content_type": "text"}, input_char)

    @add_event2dict("search_friend")
    def search_friend_result(self, header_dict, body):
        """
        服务器返回检索结果会调用此函数
        # todo 显示用户的名字
        """
        # print("收到返回搜索好友结果", header_dict, body)
        new_user_list = []
        if header_dict and body and isinstance(body, tuple):
            for each_user in body:
                if each_user:  # 当列表不为空
                    new_user_list.append(each_user[0])
        self.input_ip.configure(values=new_user_list)
        self.input_ip.event_generate("<Down>")  # 显示列表框内容

    # +++++++++++++++++++++++++++++++++++++++收到消息++++++++++++++++++++++++++++
    @add_event2dict("recv_message")
    def recv_message_result(self, header_dict, body):
        # print("收到某人的消息。。。", header_dict, body)
        if "from_account" in header_dict:
            from_account = header_dict["from_account"]
            recv_time = header_dict["time"]
            if from_account not in self.contact_listbox.item_dict:
                # print("用户不存在，添加好友中")
                self.add_new_friend(from_account)
            # print("检查好友box", self.contact_listbox.item_dict)
            self.contact_listbox.create_message(from_account, "w", "s", body, contact_time=recv_time.split(" ")[-1])
            

    # +++++++++++++++++++++++++++++++++++++++收到消息++++++++++++++++++++++++++++
    @add_event2dict("get_message")
    def get_message_result(self, header_dict, body):
        if body:
            if header_dict["type"]=="message":
                self.recv_message_result(header_dict, body)
            elif header_dict["type"]=="file":
                header_dict["file_name"] = body
                self.recv_file(header_dict, body)

    def get_message(self):
        self.sent_event(
            {"event": "get_message", "cookie": self.cookie, "content_type": "text"}, "")

# +++++++++++++++++++++++++++++++++++++++发送消息++++++++++++++++++++++++++++
    @add_event2dict("send_message")
    def send_message_result(self, header_dict, body):
        # todo 界面上显示消息发送成功或者失败结果
        # print("收到用户信息结果", header_dict, body)
        if "error" in header_dict:
            self.contact_listbox.create_message(header_dict["target_account"], "e", "s", f"发送失败{header_dict['error']}",
                                                photo_path=self.my_photo_path)
            # print("消息发送失败", body)
        else:
            # print("消息发送成功", header_dict, body, type(body))
            sent_time = changelocaltimeToSqldatetime()
            # print("更新好友时间", sent_time)
            self.update_friend(0, header_dict["target_account"], sent_time)

    def send_message(self, event):
        if self.entry_control_return_flag:  # 如果按下了control，不发送消息，防止调用改变高度函数时也调用了此发送函数
            self.entry_control_return_flag = False
        else:
            data = self.entry_message.get("1.0", tk.END)
            data = self.remove_start_enter(data)
            data = self.remove_end_enter(data)
            if data != "":
                target_account = self.contact_listbox.current_select
                if target_account is not None:
                    self.entry_message.delete('1.0', tk.END)
                    self.entry_message.index("1.0")  # 回到最初定位
                    message_ID = self.contact_listbox.create_message(target_account, "e", "s", data,
                                                                     photo_path=self.my_photo_path)
                    self.sent_event({"event": "send_message", "cookie": self.cookie,
                                      "target_account": target_account, "content_type": "text"},
                                     data)
                else:
                    tk.messagebox.showinfo("Hi", "select a friend first!")


# +++++++++++++++++++++++++++++++++++++++接收和发送文件++++++++++++++++++++++++++++
    def change_message_UI(self, message_ID, account, value, file_path=''):
        chat_window = self.contact_listbox.item_dict[account]["chat_window"]  # 聊天窗
        canvas_message_list = chat_window.canvas_message_list  # 聊天窗消息列表
        index = chat_window.get_item_index(message_ID)  # 消息在消息列表中的索引
        message_dict = canvas_message_list[index]  # 聊天窗的索引为message_index的消息
        persent_ID = message_dict["item_list"][2]  # 该消息对应的百分比ID
        image_ID = message_dict["item_list"][1] 
        chat_window.chat_canvas.itemconfigure(persent_ID, text=value)
        if file_path:
            # print("删除图标", message_ID, type(message_ID))
            self.contact_listbox.item_dict[account]["chat_window"].delete_message(int(message_ID))
            image_path, image_width, file_name, link = self.get_image_and_width(file_path)
            # print("重新创建图标", image_path, image_width, file_name, link, self.friend_dict[account]["photo"])
            time.sleep(1)
            self.contact_listbox.create_message(account, "w", "s", data="",
                                                # photo_path=self.friend_dict[account]["photo"],
                                                image_path=image_path,
                                                image_width=image_width,
                                                persent=f"{file_name}  {value}",
                                                link=link)

    @add_event2dict("get_file")
    def get_file_result(self, header_dict, body):
        # print("获取文件结果", header_dict, body)
        from_account = ""
        file_name, file_path = '', ''
        if "file_path" in header_dict:
            file_path = header_dict['file_path']
            file_name = os.path.basename(file_path)
            from_account = header_dict['from_account']
        if "error" in header_dict:
            result = "接收失败"
            result_info = f"文件{file_name}接收失败 {header_dict['error']}"
        else:
            result = "已接收"
            result_info = f"文件{file_name}接收完成"
        if "message_ID" in header_dict:
            # print(f"收到{header_dict['from_account']}的文件, 正在修改显示图标", time.time())
            self.change_message_UI(header_dict["message_ID"], header_dict["from_account"], result, file_path)
            # print(time.time())


    @add_event2dict("send_file")
    def send_file_result(self, header_dict, body):
        # print("发送文件结果", header_dict)
        file_name = ''
        if "error" not in header_dict:
            if "file_path" in header_dict:
                file_name = os.path.basename(header_dict['file_path'])
            sent_time = changelocaltimeToSqldatetime()
            self.update_friend(0, header_dict["target_account"], sent_time)
            result = "已发送"
            result_info = f"{file_name}发送成功"
        else:
            result = "发送失败"
            result_info = f"{file_name}发送失败{header_dict['error']}"

        if "message_ID" not in header_dict:
            self.contact_listbox.create_message(header_dict["target_account"], "e", "s", result,
                                                photo_path=self.my_photo_path)
        else:
            self.change_message_UI(header_dict["message_ID"], header_dict["target_account"], result)


    def get_file(self, header_dict=None):
        if header_dict is None:
            header_dict = {}
        header_dict["event"] = "get_file"
        header_dict["cookie"] = self.cookie
        self.sent_event(header_dict, "")

    def add_new_friend_call_back_for_recv_file(self, from_account, recv_time, image_path, image_width, file_name, link,
                                               header_dict):
        message_ID = self.contact_listbox.create_message(from_account, "w", "s",
                                                         data="",
                                                         contact_time=recv_time.split(" ")[-1],
                                                         image_path=image_path,
                                                         image_width=image_width,
                                                         persent=f"{file_name} 接收中",
                                                         link=link)
        header_dict["message_ID"] = message_ID
        self.get_file(header_dict)

    @add_event2dict("recv_file")
    def recv_file(self, header_dict, body):
        # print("收到某人的文件。。。", header_dict, body)
        if "from_account" in header_dict:
            from_account = header_dict["from_account"]
            recv_time = header_dict["time"]
            image_path, image_width, file_name, link = self.get_image_and_width(header_dict["file_name"])
            if from_account not in self.contact_listbox.item_dict:
                self.add_new_friend(from_account)
            message_ID = self.contact_listbox.create_message(from_account, "w", "s",
                                                         data="",
                                                         contact_time=recv_time.split(" ")[-1],
                                                         image_path=image_path,
                                                         image_width=image_width,
                                                         persent=f"{file_name} 接收中",
                                                         link=link)
            # 获取文件
            header_dict["message_ID"] = message_ID
            self.get_file(header_dict)


    def get_image_and_width(self, file_path):
        """
        文件不存在则看不见消息
        """
        self.file_image_path = os.path.join(self.HS_directory.tool_picture_dir, "file.png")
        self.files_image_path = os.path.join(self.HS_directory.tool_picture_dir, "files.png")
        self.directory_image_path = os.path.join(self.HS_directory.tool_picture_dir, "directory.png")
        self.unknow_image_path = os.path.join(self.HS_directory.tool_picture_dir, "unknown.png")
        check_list = [".png", ".jpg", ".jepg", ".PNG", ".JPG", ".JEPG"]
        if os.path.isfile(file_path):
            if not (os.path.splitext(file_path)[-1] in check_list):  # 文件
                image_path = self.file_image_path
                image_width = int(self.screenwidth * 0.03)
            else:  # 图片
                image_path = file_path
                image_width = int(self.screenwidth * 0.16)
            file_name = os.path.basename(file_path)
            link = file_path
        elif os.path.isdir(file_path):  # 文件夹
            image_path = self.directory_image_path
            image_width = int(self.screenwidth * 0.03)
            file_name = os.path.basename(file_path)
            link = file_path
        else:
            image_path = self.unknow_image_path
            image_width = int(self.screenwidth * 0.03)
            file_name = os.path.basename(file_path)
            link = ''
        # print("发送文件图片尺寸", image_width)
        return image_path, image_width, file_name, link

    def send_file_(self, file_path, target_account, send_time):
        """
        my_tcp 模块的发送文件函数会自动判断file_path是文件还是目录
        从服务器获取到收件地址， 会自动启动文件发送
        """
        # print("GUI发送文件")
        image_path, image_width, file_name, link = self.get_image_and_width(file_path)
        if image_path is None:
            return
        message_ID = self.contact_listbox.create_message(target_account, "e", "s",
                                                             data="",
                                                             photo_path=self.my_photo_path,
                                                             image_path=image_path,
                                                             image_width=image_width,
                                                             persent=f"{file_name} 发送中",
                                                             link=link)
        self.sent_event({"event": "send_file", "cookie": self.cookie, "target_account": target_account, "message_ID": message_ID, 
                          "file_path": file_path, "content_type": "file"}, "")

    def send_file_directory(self, file_directory):
        """
        发送文件或者目录
        """
        target_account = self.contact_listbox.current_select
        send_time = changelocaltimeToSqldatetime()
        if target_account is not None:
            if "tuple" in str(type(file_directory)):
                for each_file in file_directory:
                    self.send_file_(each_file, target_account, send_time)
            else:
                self.send_file_(file_directory, target_account, send_time)
        else:
            tk.messagebox.showinfo("Hi", "select a friend first!")

    def send_file(self, event=None):
        """
        发送多个文件, 选择文件后返回的是一个列表
        """
        file_path = tkfile.askopenfilenames(title="choose files to send")
        if len(file_path) > 0:
            self.send_file_directory(file_path)

    def send_directory(self, event=None):
        """
        发送单个文件夹，选择文件夹后返回的是文件夹路径字符串
        """
        directory = tkfile.askdirectory(title="chose a directory to send")
        if directory != "":
            self.send_file_directory(directory)


    # ++++++++++++++++++++++++++++++++++++++重新登录++++++++++++++++++++++++++++++++
    @add_event2dict("relogin")
    def relogin_result(self, header_dict=None, body=''):
        # print("重新登录成功")
        if header_dict["result"]:
            self.cookie = header_dict["cookie"]

    @add_event2dict("relogin_event")
    def relogin_event(self, header_dict=None, body=''):
        self.sent_event({"event": "relogin", "cookie": self.cookie, "content_type": "text"}, "")

    @add_event2dict("login_in_other_place")
    def relogin_event(self, header_dict=None, body=''):
        tk.messagebox.showinfo("Hi", "有人尝试从其他地方登录你的账号")

    # ++++++++++++++++++++++++++++++++++++++好友信息变更提醒++++++++++++++++++++++++++++++++
    @add_event2dict("user_info_change")
    def user_info_change(self, header_dict=None, body=''):
        # print("有好友信息变更")
        if body:
            # print("变更信息的好友是", body)
            [account, name, sign, photo, is_online,
                birthday, gender, address, phone, mail] = list(body)
            self.friend_dict[account] = {"account": account,
                                         "name": name, "sign": sign, "photo": photo, "is_online": is_online,
                                         "birthday": birthday,
                                         "gender": gender, "address": address, "phone": phone, "mail": mail,
                                         "nickname": self.friend_dict[account]["nickname"], "time": self.friend_dict[account]["time"]
                                         }
            # print("更新该好友信息")
            self.update_friend(0, account)
            self.HS_directory.write_user_info_file(self.account, {"friend_dict": self.friend_dict})

# ++++++++++++++++++++++++++++++++ 通讯接口 ++++++++++++++++++++++++++++
    def sent_event(self, header_dict, body):
        # print("GUI发送事件", header_dict) 发不出去可能会导致卡住, 比如客户端进程被杀死的时候(一台电脑双开两个此工具，
        # 因为此工具自带杀端口功能，所以后面开启的工具会杀掉前面开启的工具的客户端进程)
        try:
            self.q_sent.put([header_dict, body], timeout=1)
        except Exception as e:
            print("发送事件超时", str(e))

    def get_q(self):
        while True:
            try:
                recv_data = self.q_recv.get()  # 阻塞
                header_dict, body = recv_data[0], recv_data[1]
                # body = recv_data[1]
                # print("主界面收到事件返回数据", header_dict, body)
                # print("我是多线程", threading.current_thread())
                if "event" in header_dict and header_dict["event"] in event_dict:
                    # self.root.after_idle(event_dict[header_dict["event"]], self, header_dict, body)  # 此为多线程
                    # print("注册函数")
                    event_dict[header_dict["event"]](self, header_dict, body)
                    time.sleep(0.2)  # 防止连续IO事件导致界面卡顿
            except Exception as e:
                traceback.print_exc()
                # print("主界面处理事件失败", str(e))
