userinfoGUI
import os
import threading
from time import sleep
import tkinter as tk
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import time
from multiprocessing import Queue

from haimeng_tk import change_photo
from HS_universal.haimeng_time import *
from HS_universal.HS_directory import HS_directory

class User_info_GUI:
    def __init__(self, **kwargs):
        self.root = tk.Toplevel()
        self.init_GUI()
        self.create_user_info_GUI()
        self.root.resizable(0, 0)  # 锁定界面尺寸，不允许改变

    def init_GUI(self):
        # GUI 参数
        self.root.title("")
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.root_width = int(self.screenwidth * 0.22)
        self.root_height = int(self.screenheight * 0.55)

        # self.root.geometry('%sx%s' % (self.root_width, self.root_height))
        self.root.geometry('+%s+%s' % (int((self.screenwidth - self.root_width) / 2),
                                       int((self.screenheight - self.root_height) / 2)))  # 在屏幕中间开启窗口

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.avatar_frame = tk.Frame(self.root)
        self.avatar_frame.grid(row=0,column=0,sticky="we")
        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=1,column=0,sticky="wnse")
        self.save_frame = tk.Frame(self.root)
        self.save_frame.grid(row=2,column=0,sticky="n")

    def create_user_info_GUI(self):
        self.my_info_and_Entry_list = [{"key": "photo", "key_name": "photo", "value": ""},
                             {"key": "name", "key_name": "姓名：", "value": "", "label": None, "entry": None},
                             {"key": "remark", "key_name": "备注：", "value": "", "label": None, "entry": None},
                             {"key": "sign", "key_name": "签名：", "value": "", "label": None, "entry": None},
                             {"key": "birthday", "key_name": "生日：", "value": "", "label": None, "entry": None},
                             {"key": "gender", "key_name": "性别：", "value": "", "label": None, "entry": None},
                             {"key": "address", "key_name": "地址：", "value": "", "label": None, "entry": None},
                             {"key": "phone", "key_name": "电话：", "value": "", "label": None, "entry": None},
                             {"key": "mail", "key_name": "邮件：", "value": "", "label": None, "entry": None},
                             {"key": "password", "key_name": "密码：", "value": "", "label": None, "entry": None}
                             ]
        self.info_frame.columnconfigure(1,weight=1)
        i = 0
        for each_key in self.my_info_and_Entry_list:
            if i == 0:
                self.my_photo_label = tk.Label(self.avatar_frame)
                self.my_photo_label.grid(row=0, column=0, pady=5, sticky="nsew")
                i += 1
                continue
            self.my_info_and_Entry_list[i]["label"] = tk.Label(self.info_frame, text=self.my_info_and_Entry_list[i]["key_name"])
            self.my_info_and_Entry_list[i]["label"].grid(row=i, column=0, sticky="w")
            self.my_info_and_Entry_list[i]["entry"] = tk.Entry(self.info_frame,
                                                     # state="normal",
                                                     highlightbackground="gray",
                                                     borderwidth=0,
                                                     highlightcolor="gray",
                                                     highlightthickness=0.1)
            self.my_info_and_Entry_list[i]["entry"].grid(row=i, column=1, sticky="we")
            i += 1
        self.save_button = tk.Button(self.save_frame, text="保存")
        self.save_button.grid(row=i, column=0, pady=10, sticky="n")
        self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)

    def close_GUI(self):
        self.root.destroy()


class User_info_app(User_info_GUI):
    have_instace = None  # 只能创建一个这种界面

    def __new__(cls, owner_account, sent_event_fun, **kwargs):
        if cls.have_instace is None:
            cls.have_instace = super().__new__(cls)
            return cls.have_instace

    def __init__(self, owner_account, cookie, sent_event_fun, **kwargs):
        """
        这个类用来：
            给它一组包含账户信息的数据（列表），它就能显示出来
            当点击头像时，可以更换头像
            当点击保存时，可以保存用户信息
        入口参数： 当前显示的账号， 好友信息字典， 主人账号
        """
        super().__init__(**kwargs)
        # << -------------------------  初始化 获取账户和对应的头像、信息 ———
        self.HS_directory_obj = HS_directory()
        self.sent_event = sent_event_fun
        self.owner_account = owner_account
        self.cookie = cookie

        self.is_owner_account = False
        self.account = kwargs["account"]  # 指定查询谁的信息

        self.my_photo_name = kwargs["photo"]  # 指定该用户头像
        print("我的头像明字", self.my_photo_name)
        self.my_photo_path = os.path.join(str(self.HS_directory_obj.user_avartar_dir), self.my_photo_name)
        if not self.my_photo_name or not os.path.exists(self.my_photo_path):
            self.my_photo_path = self.HS_directory_obj.default_avatar  # 默认头像
        print("我的头像是", self.my_photo_path)
        self.my_photo = self.update_avatar(self.my_photo_path)
        # ------------------------------------------------------------->>
        # 判断是不是当前登录账号
        if self.account == self.owner_account:
            # << ---------------  绑定更换头像 和 修改信息事件 --------------
            self.is_owner_account = True
            self.entry_state = "normal"
            self.my_photo_label.bind("<ButtonPress-1>", self.choose_new_photo)  # 绑定更换头像事件
            self.my_photo_label2 = tk.Label(self.avatar_frame, text="点我换头像", fg="white", bg="orange")
            self.my_photo_label2.grid(row=0, column=0, pady=5, sticky="se")
            self.my_photo_label2.bind("<ButtonPress-1>", self.choose_new_photo)
            # -------------------------------------------->>
            # 待插入的信息列表
            self.insert_info_list = [   
                                        kwargs["photo"], kwargs["name"], kwargs["nickname"],
                                        kwargs["sign"], kwargs["birthday"], kwargs["gender"],
                                        kwargs["address"], kwargs["phone"], kwargs["mail"],
                                        ""
            ]
        else:
            self.entry_state = "readonly"
            # <<--------- 不显示密码 ---------------- 
            self.my_info_and_Entry_list[-1]["entry"].grid_forget()
            self.my_info_and_Entry_list[-1]["entry"].destroy()  
            self.my_info_and_Entry_list[-1]["label"].destroy()
            self.my_info_and_Entry_list = self.my_info_and_Entry_list[:-1]
            # ----------------------------------->>
            self.insert_info_list = [
                                        kwargs["photo"], kwargs["name"], kwargs["nickname"],
                                        kwargs["sign"], kwargs["birthday"], kwargs["gender"],
                                        kwargs["address"], kwargs["phone"], kwargs["mail"]
            ]
        print("用户信息是", self.insert_info_list)
        # --------------  绑定保存信息事件 --------------
        self.new_photo_path = ""  # 当此值不为空，说明用户更换了头像
        self.save_button["command"] = self.save_info  # 绑定保存事件
        # ------------  显示用户信息 -------------
        self.insert_user_info()

    def update_avatar(self, photo_path):
        self.my_photo = change_photo(photo_path, int(self.screenwidth * 0.22), is_zoomout=True, is_square=True)[0]
        print("正在更新我的头像", photo_path, self.my_photo)
        if self.my_photo is not None:
            self.my_photo_label.configure(image=self.my_photo)
        return self.my_photo

    def insert_user_info(self):
        for i, each_info in enumerate(self.my_info_and_Entry_list):
            if i == 0:  # 头像不需要
                continue
            if self.insert_info_list[i] is not None:
                self.my_info_and_Entry_list[i]["value"] = self.insert_info_list[i]
                self.my_info_and_Entry_list[i]["entry"].insert(0, self.my_info_and_Entry_list[i]["value"])
            if each_info["key"] != "remark":  # 遇到nick_name j 不加1
                self.my_info_and_Entry_list[i]["entry"]["state"] = self.entry_state
            else:
                self.my_info_and_Entry_list[i]["entry"]["state"] = "normal"
            if each_info["key"] == "password":
                print("不显示密码")
                self.my_info_and_Entry_list[i]["entry"]["show"] = "*"
        self.insert_avatar(self.insert_info_list[0])  # 插入头像

    def insert_avatar(self, photo):
        """
        获取到的头像和现在的头像不一致时， 更新头像， 如果本地没有新头像， 从服务器申请下载
        """
        if photo and os.path.basename(self.my_photo_path) != photo:  # 只有获取到的头像和现在的头像不一致时
            new_photo_path = os.path.join(self.HS_directory_obj.user_avartar_dir, photo)
            if os.path.exists(new_photo_path):
                self.my_photo_path = new_photo_path
                self.update_avatar(self.my_photo_path)
            else:
                print("从服务器下载头像...")

    def save_info(self):
        """
        检查用户是否修改了个人信息， 头像和好友备注
        self.my_info_and_Entry_list[i]["key"]： key名和数据库的键名是一样的
        """
        modify_dict = {}
        i = 0
        for j in self.my_info_and_Entry_list:
            if i == 0:
                i += 1
                continue
            if self.my_info_and_Entry_list[i]["value"] != self.my_info_and_Entry_list[i]["entry"].get():
                modify_dict[self.my_info_and_Entry_list[i]["key"]] = self.my_info_and_Entry_list[i]["entry"].get()
            i += 1
        if "remark" in modify_dict:  # 如果用户修改了好友备注
            print("修改备注")
            self.sent_event({"event": "modify_friend_info", "cookie": self.cookie, "target_account": self.account,
                             "modify_dict":{"nickname": modify_dict["remark"]}, "content_type": "text"}, "")
            modify_dict.pop("remark")
        if modify_dict != {}:  # 如果用户修改了个人信息
            print("修改个人信息", modify_dict)
            self.sent_event({"event": "modify_my_info", "cookie": self.cookie, "from_account": self.account,
                             "modify_dict": modify_dict, "content_type": "text"}, "")
        # 如果需要更改头像
        if self.new_photo_path != "":
            self.new_photo_path = self.copy_photo_to_userdata()  # 复制头像到程序所在目录
            self.sent_event({"event": "change_my_avatar", "cookie": self.cookie, "from_account": self.account,
                             "file_path": self.new_photo_path, "content_type": "text"}, "")
        self.close_GUI()

    def choose_new_photo(self, event):
        """
        将选择的文件路径保存到self.new_photo_path 并暂时更换头像
        """
        file_path = tkfile.askopenfilename(title="选择图片作为你的头像")
        check_list = [".jpg", ".png", ".JPG" ]
        if file_path != "" and (os.path.splitext(file_path)[-1] in check_list):
            self.new_photo_path = file_path
            self.update_avatar(self.new_photo_path)
        elif file_path != "":
            tkmessage.showinfo("Hi", "请选择.png或者.jpg文件")

    def generate_new_photo_name(self):
        """
        生成新的特殊的头像名称
        """
        current_time = str(int(time.time()))
        if ".png" in self.new_photo_path:
            new_photo_name = self.account + current_time + ".png"
        elif ".jpg" in self.new_photo_path:
            new_photo_name = self.account + current_time + ".jpg"
        else:
            new_photo_name = "error"
        return new_photo_name

    def copy_photo_to_userdata(self):
        """
        复制文件到用户头像路径
        """
        new_photo_name = self.generate_new_photo_name()
        with open(self.new_photo_path, "rb") as old_f:
            old_f_data = old_f.read()
        new_photo_path = os.path.join(self.HS_directory_obj.user_avartar_dir, new_photo_name)
        with open(new_photo_path, "wb") as new_f:
            new_f.write(old_f_data)
        return new_photo_path

    def change_user_photo_success(self):
        """
        服务器返回头像修改成功的通知
        如果旧头像存在则删除
        """
        if os.path.exists(self.my_photo_path):
            try:
                os.remove(self.my_photo_path)
            except Exception as e:
                print(f"删除旧头像失败{str(e)}，请手动删除，路径是{self.my_photo_path}")
        self.my_photo_path = self.new_photo_path

    def close_GUI(self):
        User_info_app.have_instace = None
        self.root.destroy()
