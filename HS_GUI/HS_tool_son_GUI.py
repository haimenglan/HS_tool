# 自带模块
import os
import sys
import time
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkmessage
import tkinter.font as tkFont
import tkinter.filedialog as tkfile
import platform
import threading
import pickle

#print("当前操作系统是：", platform.system())
if platform.system() == "Windows":
    import ctypes
    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    #print("缩放系数是", ScaleFactor)
# 我的库
from haimeng_tk import *
from HS_universal.haimeng_time import *
from HS_universal.HS_directory import HS_directory

from HS_tool_tool import UnitdetailsDataTool
from HS_tool_tool import draw_picture
from HS_tool_tool.compare_rush import Compare_rush
from HS_tool_tool.miaobiao import Miaobiao
from HS_tool_tool.compare_overlay_FOMs import Insight_csv,Overlay_compare_fom,My_xlwt
from HS_tool_tool.DUT_communicationGUI import My_serial
from HS_tool_tool.find_records_csv_item import Rcords_csv
# from HS_tool_tool.send_file import SendFileApp

class Contact_listbox(Haimeng_listbox):
    def __init__(self, root, chat_name_frame, chat_window_frame, width=None, height=None):
        """
        这个类将联系人列表与聊天窗进行组合
        """
        super().__init__(root, width, height)
        self.HS_directory = HS_directory()
        self.current_select = None
        self.item_dict = {}
        self.lock = threading.Lock()
        self.chat_name_frame = chat_name_frame  # 聊天窗名字
        self.chat_window_frame = chat_window_frame  # 聊天窗
        # 初始化字体，背景色
        if platform.system() == "Windows":
            self.friend_name_ft = tkFont.Font(family='微软雅黑', size=14)
            self.sign_ft = tkFont.Font(family='微软雅黑', size=10)
        else:
            self.friend_name_ft = tkFont.Font(family='微软雅黑', size=16)
            self.sign_ft = tkFont.Font(family='微软雅黑', size=12)
        self.chat_name_bg = color_change(245,245,245)
        self.chat_window_bg = color_change(245, 245, 245)
        # 创建白板，用来遮挡聊天窗过长的名字
        self.empty_label_frame = tk.Frame(self.chat_name_frame, bg=self.chat_name_bg)
        self.empty_label_frame.grid(row=0, column=0, columnspan=2, sticky="wnse")
        self.empty_label = tk.Label(self.empty_label_frame, text=" ",font=self.friend_name_ft, bg=self.chat_name_bg)
        self.empty_label.pack(fill="both")
        self.chat_name_frame.columnconfigure(1, weight=1)

    def create_chat_window(self, name, sign):
        # 创建账户对应的名字，签名，聊天窗
        name_label = tk.Label(self.chat_name_frame, text=name, font=self.friend_name_ft,bg=self.chat_name_bg)
        name_label.grid(row=0, column=0,padx=10, sticky="w")
        sign_label = tk.Label(self.chat_name_frame, text=sign, font=self.sign_ft, fg="gray",bg=self.chat_name_bg)
        sign_label.grid(row=0, column=1,pady=10, sticky="ws")
        chat_window = Haimeng_chat_window(self.chat_window_frame, bg=self.chat_window_bg)
        chat_window.grid(0, 0, sticky="ewns")
        return name_label, sign_label, chat_window

    def insert(self, index, image_path, name, sign, time_str, message, status, account):
        """
        使用线程锁，防止多个线程同时插入一个账户
        当账户未插入，才新增选项
        self.item_dict = {"account":
                                    {"item":选项框架,
                                     "sign":签名,
                                     "chat_name_label":聊天窗的名字,
                                     "chat_window":聊天窗
                                     }
                          }
        """
        self.lock.acquire()
        if account not in self.item_dict:
            self.item_dict[account] = {}
            item = super().insert(index, image_path, name, time_str, message, status, account)
            self.item_dict[account]["item"] = item
            self.item_dict[account]["sign"] = sign
            name_label,sign_label,chat_window = self.create_chat_window(name,sign)
            self.item_dict[account]["chat_name_label"] = name_label
            self.item_dict[account]["chat_sign_label"] = sign_label
            self.item_dict[account]["chat_window"] = chat_window
            self.lock.release()
        else:
            self.lock.release()
            return False
        # 聊天界面仍然显示原来选择的好友
        self.empty_label_frame.tkraise()
        if self.last_select is not None:
            account = self.item_list[self.last_select].item_name
            self.item_dict[account]["chat_name_label"].tkraise()
            self.item_dict[account]["chat_sign_label"].tkraise()
            self.item_dict[account]["chat_window"].tkraise()
        return True

    def delete_item(self, account, item, event=None):
        try:
            super().delete_item(item)
            self.item_dict[account]["chat_name_label"].destroy()
            self.item_dict[account]["chat_sign_label"].destroy()
            self.item_dict[account]["chat_window"].chat_canvas.destroy()
            if self.last_select == item.index:
                self.empty_label_frame.tkraise()
            self.item_dict.pop(item.item_name)
        except Exception as e:
            print("删除好友出错", str(e))


    def selecte_item(self, ID, account):
        self.current_select = account
        self.empty_label_frame.tkraise()
        self.item_dict[account]["chat_name_label"].tkraise()
        self.item_dict[account]["chat_sign_label"].tkraise()
        self.item_dict[account]["chat_window"].tkraise()
        super().selecte_item(ID, account)

    def create_message(self, account, xside, yside, data, **kwargs):
        """
        参数解释：
            账号对应聊天窗， xside，yside对应信息在聊天窗的方向，data要显示的消息内容
            photo_path对应头像路径（注意区分我的头像还是对方的头像）
        """
        if "photo_path" not in kwargs:
            photo_path = self.item_dict[account]["item"].image_path
        else:
            photo_path = kwargs["photo_path"]
        message_index = \
            self.item_dict[account]["chat_window"].create_message(photo_path, xside, yside, data, **kwargs)
        contact_time, notice_mark = "", ""
        if "contact_time" in kwargs:
            contact_time = kwargs["contact_time"]
        else:
            contact_time = changelocaltimeToSqldatetime().split(" ")[-1]
        if self.last_select != self.item_dict[account]["item"].index:
            notice_mark = "未读"
        self.update_user_info(account, message=data, time=contact_time, notice_mark=notice_mark)
        return message_index


    def update_user_info(self, account, **kwargs):
        """
        更新联系人列表的好友消息标记，头像，名字，信息，时间，在线状态
        """
        if "notice_mark" in kwargs:
            if kwargs["notice_mark"] == "未读":
                self.item_dict[account]["item"].notice_mark["fg"] = "red"
        if "image_path" in kwargs:
            self.item_dict[account]["item"].image_path = kwargs["image_path"]
            self.item_dict[account]["item"].tk_image = change_photo(self.item_dict[account]["item"].image_path,
                                                    int(self.screenwidth * 0.0256),is_zoomout=True,is_square=True)[0]
            self.item_dict[account]["item"].tk_image_label["image"] = self.item_dict[account]["item"].tk_image
        for each_label in ["name","message","contact_time"]:
            if each_label in kwargs:
                if each_label == "name":
                    self.item_dict[account]["item"].name_label["text"] = kwargs[each_label]
                    self.item_dict[account]["chat_name_label"]["text"] = kwargs[each_label]
                elif each_label == "message":
                    self.item_dict[account]["item"].message_label["text"] = kwargs[each_label][:15]
                elif each_label == "contact_time":
                    self.item_dict[account]["item"].time_label["text"] = kwargs[each_label]

        if "status" in kwargs:
            self.item_dict[account]["item"].status_label["fg"] = self.item_dict[account]["item"].status_color[kwargs["status"]]
            self.item_dict[account]["item"].status_label["text"] = kwargs["status"]
        # 更新聊天窗
        if "sign" in kwargs:
            self.item_dict[account]["chat_sign_label"]["text"] = kwargs["sign"]
        if "index" in kwargs:
            self.update_item_index(self.item_dict[account]["item"].index, kwargs["index"])



class HS_tool_tool:
    def __init__(self,HS_tool_setting_app):
        self.HS_tool_setting_app = HS_tool_setting_app
        self.setting_value_dict = self.HS_tool_setting_app.read_setting_dict()
        # print("当前设置字典是",self.setting_value_dict)

    #  ================  tool 函数 ====================
    def daily_report_tool(self):
        csv_path = tkfile.askopenfilename(title="choose unitdetails csv file")
        if csv_path!="":
            # print("启动daily report")
            show_empty = self.setting_value_dict["daily report"]["show_empty"]
            is_change_config = self.setting_value_dict["daily report"]["is change config"]
            is_FBR_config = self.setting_value_dict["daily report"]["is FBR config"]
            is_platinum = self.setting_value_dict["daily report"]["is platinum"]
            station_list= self.setting_value_dict["daily report"]["entry_value"]
            print("站位列表是", station_list)
            # print("****",str(type(show_empty)),is_change_config,is_FBR_config)
            new_station_list = []
            if ";" in station_list:
                station_list = station_list.split(";")
                print("站位列表是", station_list)
                for each_station in station_list:
                    current_station = each_station
                    while current_station and " " == current_station[-1] or "\n" == current_station[-1]:
                        current_station = current_station[:-1]
                    while current_station and " " == current_station[0] or "\n" == current_station[0]:
                        current_station = current_station[1:]
                    new_station_list.append(current_station)
            print("站位列表是", new_station_list)
            
            xls_save_path = tkfile.asksaveasfilename(title="选择保存位置和名称", defaultextension=".xls")
            csv_file_path_multi = ""
            if show_empty:
                csv_file_path_multi = tkfile.askopenfilename(
                    title="choose MultitType UnitTestDetails or insight export data which include fail sn")
                if csv_file_path_multi=="":
                    return
            FBR_xls_file = ""
            if is_FBR_config:
                FBR_xls_file = tkfile.askopenfilename(title="选择LA2x_FRB_QT Dmin_value_table")
                if FBR_xls_file:
                    return
            UnitdetailsDataTool.run_daily_report(csv_path, xls_save_path, show_empty,is_change_config ,
                                                 is_FBR_config,FBR_xls_file,csv_file_path_multi, is_platinum=is_platinum, order_station_list=station_list)

    def draw_test_item_picture(self):
        csv_file_path_list = tkfile.askopenfilenames(title="选择单个或多个 csv数据 文件")
        if csv_file_path_list != "":
            # if platform.system()=="Darwin":
                # os.system(f'python3 {sys.path[0]+os.sep}pak{os.sep}HS_tool_tool{os.sep}draw_picture.py "{str(csv_file_path_list)}"')
                # print("已经启动画图")
            draw_picture.main(csv_file_path_list)
                # draw_picture.run_draw_picture(csv_file_path_list)

    def compare_rush(self):
        compare_rush = Compare_rush()
        compare_rush.start_compare()

    def overlay_FOMs_tool(self):
        por_path = tkfile.askopenfilename(title="choose POR version insight export csv file path")
        new_path = tkfile.askopenfilename(title="choose NEW version insight export csv file path")
        if new_path != "":
            save_path = os.path.dirname(new_path)
            overlay_compare_fom = Overlay_compare_fom(por_path, new_path)
            my_xlwt = My_xlwt(save_path)
            my_xlwt.write_compare_fom_result(overlay_compare_fom)
            my_xlwt.write_compare_data_result(overlay_compare_fom)
            tkmessage.showinfo("Hi", "Result file have saved at %s" % (save_path))

    def find_records_csv(self):
        data_directory = tkfile.askdirectory(title='choose data path')
        if data_directory != "":
            search_mode = self.setting_value_dict["Find records_csv"]["指定测试项"]
            row_column_mode = self.setting_value_dict["Find records_csv"]["横排/竖排"]
            find_name = self.setting_value_dict["Find records_csv"]["entry_value"]
            find_name_list = []
            if ";" in find_name:
                find_list = find_name.split(";")
                # print("站位列表是", station_list)
                for each_station in find_list:
                    current_station = each_station
                    while current_station and " " == current_station[-1] or "\n" == current_station[-1]:
                        current_station = current_station[:-1]
                    while current_station and " " == current_station[0] or "\n" == current_station[0]:
                        current_station = current_station[1:]
                    find_name_list.append(current_station)
            records_csv = Rcords_csv(data_directory, search_mode, row_column_mode, find_name_list)
            haimeng_xlwt = Haimeng_xlwt()
            style = haimeng_xlwt.normal_style
            sheet_value_list = records_csv.search_item()
            records_csv.write_item_to_xls(sheet_value_list, style)

    def fun_timer(self):
            self.miaobiao = Miaobiao()

    def dut_communication(self):
        dut_sent_command = My_serial(self.setting_value_dict["Dut communication"]["波特率"], None)

    # def send_file(self):
    #     SendFileApp()



class HS_tool_setting:
    def __init__(self):
        # print("初始化设置界面")
        self.setting_tk_dict = {
            "daily report": {
                "show_empty": tk.IntVar(),
                "is change config": tk.IntVar(),
                "is FBR config": tk.IntVar(),
                "is platinum": tk.IntVar(),
                "entry_value": None
            },
            "Find records_csv": {
                "指定测试项": tk.IntVar(),
                "横排/竖排": tk.IntVar(),
                "entry_value": None
            },
            "Dut communication": {
                "波特率": None
            }
        }

    def create_setting_GUI(self,**kwargs):
        self.root_setting = tk.Toplevel()
        self.root_setting.title("设置")
        self.screenwidth, self.screenheight=self.root_setting.winfo_screenwidth(),self.root_setting.winfo_screenheight()
        self.root_width,self.root_height = int(self.screenwidth * 0.4),int(self.screenheight * 0.5)

        self.root_setting.geometry('%sx%s' % (self.root_width,self.root_height ))
        self.root_setting.geometry('+%s+%s' % (int((self.screenwidth - self.root_width) / 2),
                                       int((self.screenheight - self.root_height) / 2)))
        self.create_daily_report_setting(**kwargs)
        self.create_find_record_csv_setting(**kwargs)
        self.create_dut_communication_setting(**kwargs)
        self.create_account_setting(**kwargs)

        self.root_setting_frame_save = tk.Frame(self.root_setting)
        self.root_setting_frame_save.pack(side='bottom', anchor='w')
        self.save_setting_button = tk.Button(self.root_setting_frame_save, text="保存设置", width=10,
                                             command=self.save_setting).pack(side='bottom', anchor="s")
        self.root_setting_frame_save.pack(side='bottom', anchor="s")

        self.root_setting.protocol('WM_DELETE_WINDOW', self.close_setting)  # 关闭窗口时创建的方法
        # print("loop设置界面")
        self.root_setting.mainloop()

    def create_daily_report_setting(self,**kwargs):
        # self.show_empty = kwargs["daily report"]["show_empty"]
        # self.is_change_config = kwargs["daily report"]["is change config"]
        # self.is_FBR_config = kwargs["daily report"]["is FBR config"]
        frame_name = tk.Frame(self.root_setting)
        frame_name.pack(side='top', anchor='w')
        tk.Label(frame_name, text="1. Daily Report").grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky="w")
        row_num,column_num = 1,0
        for each_key in self.setting_tk_dict["daily report"]:
            if each_key!="entry_value":
                self.setting_tk_dict["daily report"][each_key].set(kwargs["daily report"][each_key])
                tk.Checkbutton(frame_name, text=each_key, variable=self.setting_tk_dict["daily report"][each_key]) \
                    .grid(row=row_num, column=column_num, padx=10, pady=5, sticky="w")
                column_num+=1
                if column_num%4==0:
                    row_num += 1
                    column_num = 0
            else:
                self.setting_tk_dict["daily report"]["entry_value"] = tk.Text(frame_name,height=8,
                                                     width=50,
                                                     bg=color_change(235, 235, 235),
                                                     highlightthickness=0,
                                                     borderwidth=0,
                                                     font='Helvetica', relief="raised")
                self.setting_tk_dict["daily report"]["entry_value"].grid(row=row_num + 2, column=0, columnspan=5, padx=10, pady=5, sticky="w")
                self.setting_tk_dict["daily report"]["entry_value"].insert("1.0",kwargs["daily report"][each_key])

    def create_find_record_csv_setting(self,**kwargs):
        # self.is_assign_item = kwargs["Find records_csv"]["指定测试项"]
        # self.horizontal_vertical = kwargs["Find records_csv"]["横排/竖排"]
        # self.entry_value = kwargs["Find records_csv"]["entry_value"]
        frame_name = tk.Frame(self.root_setting)
        frame_name.pack(side='top', anchor='w')
        tk.Label(frame_name, text="2. Find records_csv").grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky="w")
        row_num, column_num = 1, 0
        for each_key in self.setting_tk_dict["Find records_csv"]:
            if each_key!="entry_value":
                self.setting_tk_dict["Find records_csv"][each_key].set(kwargs["Find records_csv"][each_key])
                tk.Checkbutton(frame_name, text=each_key, variable=self.setting_tk_dict["Find records_csv"][each_key]) \
                    .grid(row=row_num, column=column_num, padx=10, pady=5, sticky="w")
                column_num += 1
                if column_num % 3 == 0:
                    row_num += 1
            else:
                self.setting_tk_dict["Find records_csv"]["entry_value"] = tk.Text(frame_name,height=8,
                                                     width=50,
                                                     bg=color_change(235, 235, 235),
                                                     highlightthickness=0,
                                                     borderwidth=0,
                                                     font='Helvetica', relief="raised")
                self.setting_tk_dict["Find records_csv"]["entry_value"].grid(row=row_num + 2, column=0, columnspan=5, padx=10, pady=5, sticky="w")
                self.setting_tk_dict["Find records_csv"]["entry_value"].insert("1.0",kwargs["Find records_csv"][each_key])

    def create_dut_communication_setting(self,**kwargs):
        self.root_setting_frame_DUT_setting = tk.Frame(self.root_setting)
        self.root_setting_frame_DUT_setting.pack(side='top', anchor='w')
        self.baud_rate = kwargs["Dut communication"]["波特率"]
        self.Label_DUT_setting = tk.Label(self.root_setting_frame_DUT_setting,
                                          text="3.DUT communication setting: ")
        self.Label_DUT_setting.grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky="w")
        self.Label2_DUT_setting = tk.Label(self.root_setting_frame_DUT_setting, text="波特率:")
        self.Label2_DUT_setting.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.entry_DUT_setting_var = tk.StringVar()
        self.setting_tk_dict["Dut communication"]["波特率"] = tk.Entry(self.root_setting_frame_DUT_setting,
                                          textvariable=self.entry_DUT_setting_var,
                                          width=20)
        self.setting_tk_dict["Dut communication"]["波特率"].grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.setting_tk_dict["Dut communication"]["波特率"].insert(0, kwargs["Dut communication"]['波特率'])

    def create_account_setting(self,**kwargs):
        pass

    def save_setting(self,**kwargs):
        pass

    def close_setting(self):
        self.root_setting.destroy()



class HS_tool_setting_app(HS_tool_setting):
    have_instace = None
    def __new__(cls, account=""):
        if cls.have_instace is None:
            cls.have_instace = super().__new__(cls)
            return cls.have_instace

    def __init__(self, account=""):
        # print("初始化设置")
        self.account = account
        self.HS_directory = HS_directory()
        self.setting_value_dict = self.read_setting_dict()
        super().__init__()

    def create_setting_GUI(self):
        super().create_setting_GUI(**self.setting_value_dict)

    def read_setting_dict(self):
        self.setting_file_path = os.path.join(self.HS_directory.config_dir, f"{self.account}_settings")
        try:
            with open(self.setting_file_path, "rb") as f:
                self.setting_value_dict = pickle.load(f)
        except:
            self.setting_value_dict = {
                "daily report": {
                    "show_empty": 0,
                    "is change config": 0,
                    "is FBR config": 0,
                    "is platinum": 0,
                    "entry_value": "在此输入站位以排序,用分号隔开不同站位"
                },
                "Find records_csv": {
                    "指定测试项": 0,
                    "横排/竖排": 0,
                    "entry_value": "在此输入测项,用分号隔开"
                },
                "Dut communication": {
                    "波特率": 115200
                }
            }
        return self.setting_value_dict

    def check_is_setting_change(self):
        for each_option in self.setting_tk_dict:
            for each_key in self.setting_tk_dict[each_option]:
                if each_key!="entry_value":
                    current_value = int(self.setting_tk_dict[each_option][each_key].get())
                else:
                    current_value = self.setting_tk_dict[each_option][each_key].get("1.0", tk.END)[:-1] #去掉最后的回车
                if current_value != self.setting_value_dict[each_option][each_key]:
                    # print(f"选项改变,new{current_value},old{self.setting_value_dict[each_option][each_key]}")
                    return True
        return False

    def save_setting(self):
        is_setting_change = False
        for each_option in self.setting_tk_dict:
            for each_key in self.setting_tk_dict[each_option]:
                if each_key!="entry_value":
                    current_value = int(self.setting_tk_dict[each_option][each_key].get())
                else:
                    current_value = self.setting_tk_dict[each_option][each_key].get("1.0", tk.END)
                if current_value != self.setting_value_dict[each_option][each_key]:
                    # print(f"保存{self.setting_tk_dict[each_option][each_key]}值为{current_value}")
                    self.setting_value_dict[each_option][each_key] = current_value
                    is_setting_change = True
        if is_setting_change:
            f = open(self.setting_file_path,"wb")
            pickle.dump(self.setting_value_dict, f)
            f.close()
        HS_tool_setting_app.have_instace = None
        self.root_setting.destroy()

    def close_setting(self):
        is_setting_change = self.check_is_setting_change()
        if is_setting_change:
            yesno = tkmessage.askyesno("Hi", "是否保存设置")
            if yesno:
                self.save_setting()
        HS_tool_setting_app.have_instace = None
        self.root_setting.destroy()
