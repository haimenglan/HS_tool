import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkmessage
import os
import platform
import time
import threading

from haimeng_tk import color_change, change_photo
from HS_main_GUI import HS_tool_app
from HS_universal.HS_directory import HS_directory

if platform.system() == "Windows":
    import ctypes
    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    print("缩放系数是", ScaleFactor)
    # import pathos
    # from pathos.multiprocessing import ProcessingPool

class Login_GUI:
    def __init__(self, account="", password="", photo_path=""):
        self.account, self.password, self.photo_path = account, password, photo_path
        self.HS_directory = HS_directory()
        self.root = tk.Tk()

        # self.root.wm_withdraw()  # 隐藏部件
        self.root.title(" ")
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        if platform.system() == "Windows":
            ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(1)
            self.root.tk.call('tk', 'scaling', ScaleFactor/100)
            print("现在的缩放系数是", ScaleFactor)
            self.root_width = int(self.screenwidth * 0.18)
            self.root_height = int(self.screenwidth * 0.28)
            self.frame_padx = 30
        else:
            self.root_width = int(self.screenwidth * 0.18)
            self.root_height = int(self.screenwidth * 0.30)
            self.frame_padx = 10
        self.root.geometry('%sx%s+%s+%s' % (self.root_width, self.root_height,
                                            int((self.screenwidth - self.root_width) / 2),
                                            int((self.screenheight - self.root_height) / 2)))
        self.user_info = self.HS_directory.read_user_info_file(account)
        if self.user_info:
            if "account" in self.user_info:
                self.account, self.password= self.user_info["account"], self.user_info["password"]
            if "photo_path" in self.user_info:
                self.photo_path = self.user_info["photo_path"]
        self.create_login_GUI(self.account, self.password, self.photo_path)
        # self.root.wm_deiconify()  # 显示部件
        self.root.resizable(0, 0)

    def create_login_GUI(self, account="", password="", photo_path=""):
        # 创建整个登录界面的框架
        self.login_frame = tk.Frame(self.root)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.login_frame.grid(row=0, column=0, sticky="nwse")

        if photo_path and os.path.exists(photo_path):
            self.login_photo_path = photo_path
        else:
            self.login_photo_path = os.path.join(self.HS_directory.tool_picture_dir, "login.png")  # 默认图片
        # print("登录图片路径",self.login_photo_path)
        self.login_photo = change_photo(self.login_photo_path, int(self.root_width*0.8),
                                        height=int(self.root_width*0.8), is_zoomout=True, is_square=False)[0]
        self.login_image_label = tk.Label(self.login_frame, image=self.login_photo)
        self.login_image_label.grid(row=0, column=0, columnspan=2, pady=30, sticky="nsew")

        self.login_frame.columnconfigure(0, weight=1)
        self.login_frame.rowconfigure(2, weight=1)
        # 账号密码框架
        self.account_password_frame = tk.Frame(self.login_frame)
        self.account_password_frame.grid(row=1, column=0, padx=self.frame_padx, pady=10, sticky="we")
        account_frame_width = self.account_password_frame.winfo_width()
        # 登录按钮框架
        self.label_frame = tk.Frame(self.login_frame)  #, bg="white")
        self.label_frame.grid(row=3, column=0, padx=self.frame_padx,  sticky="wens")
        self.register_frame = tk.Frame(self.login_frame, width=account_frame_width)
        self.register_frame.grid(row=2, column=0, padx=self.frame_padx,sticky="wens")
        # 创建账号密码框
        if platform.system() == "Windows":
            self.entry_font = tkFont.Font(family='微软雅黑', size=12)  # 未读提示点的尺寸
            self.login_button_font = tkFont.Font(family='微软雅黑', size=10)
        else:
            self.entry_font = tkFont.Font(family='微软雅黑', size=14)  # 未读提示点的尺寸
            self.login_button_font = tkFont.Font(family='微软雅黑', size=13)
        self.account_label = tk.Label(self.account_password_frame, text='Account', font=self.entry_font)
        self.account_entry = tk.Entry(self.account_password_frame, font=self.entry_font)
        self.account_entry.insert(0,account)
        self.password_label = tk.Label(self.account_password_frame, text='PassWord', font=self.entry_font)
        self.password_entry = tk.Entry(self.account_password_frame,font=self.entry_font, show="*")
        self.password_entry.insert(0,password)
        # 创建登录注册按钮
        self.register_button = tk.Label(self.register_frame, text="Register", font=self.login_button_font,
                                        fg="white", bg="orange")
        self.login_button = tk.Label(self.register_frame, text=" Login ", font=self.login_button_font,
                                     fg="white", bg="orange")
        self.login_label = tk.Label(self.label_frame, text=' ', fg="orange")  # 登录结果提示信息
        # 组件布局
        self.account_password_frame.columnconfigure(1, weight=1)
        self.account_label.grid(row=0, column=0, sticky="w")
        self.account_entry.grid(row=0, column=1, sticky="we")
        self.password_label.grid(row=2, column=0, sticky="w")
        self.password_entry.grid(row=2, column=1, sticky="we")
        self.register_frame.columnconfigure(1, weight=1)
        self.register_button.grid(row=0, column=0, sticky="w", padx=20)
        self.login_button.grid(row=0, column=1, sticky="e", padx=20)
        self.label_frame.columnconfigure(0, weight=1)
        self.login_label.grid(row=0, column=0, pady=10, sticky="we")


class Login_bind_event(Login_GUI):
    def __init__(self, q_sent=None, q_recv=None, account="", password="", photo_path=""):
        '''
        1. 创建界面
        2. 绑定登录事件到按钮和回车键，不断侦测用户是否有登录操作，然后调用相应的函数 --> 已经移到HS_tool.py
        3. 其中登录成功或者登录失败函数是 主程序HS_tool_event 来调用的，因为登录的结果是由服务器告知HS_tool_event
        '''
        super().__init__(account, password, photo_path)
        # print(q_sent,q_recv)
        self.q_sent, self.q_recv = q_sent, q_recv
        self.show_login_progress_flag = False
        self.login_button.bind("<ButtonPress-1>", self.login)
        register_CMD_event = lambda event: self.register(event=event)
        self.register_button.bind("<ButtonPress-1>", register_CMD_event)
        login_CMD_event = lambda event: self.login(event=event)
        self.root.bind("<KeyPress-Return>", login_CMD_event)

    def login_fail(self, result):
        '''
        如果登录失败，显示登录按钮，绑定回车事件
        如果是从主界面重新登录失败，则销毁主界面，显示登录界面
        '''
        self.show_login_progress_flag = True
        self.login_label["text"] = result
        self.register_button.grid(row=0, column=0, sticky="w", padx=20)
        self.login_button.grid(row=0, column=1, sticky="e", padx=20)
        login_CMD_event = lambda event: self.login(event=event)
        self.root.bind("<KeyPress-Return>", login_CMD_event)

    def login_success(self):
        '''
        隐藏登录界面
        '''
        self.show_login_progress_flag = True
        self.login_label["text"] = "登录成功"
        # self.login_frame.pack_forget()
        self.login_frame.grid_forget()

    def show_login_progress(self):
        current_time = time.time()
        self.login_label["text"] = "正在登录"
        i = 0
        while time.time()-current_time<120:
            if self.show_login_progress_flag:
                break
            i += 1
            if i>20:
                i = 0
            self.login_label["text"] = "正在登录"+"."*i
            time.sleep(0.5)

    def check_account_format(self):
        self.account, self.password = self.account_entry.get()[:], self.password_entry.get()[:]
        is_meet_demand = False
        self.show_login_progress_flag = False
        if self.account != "" and self.password != "":
            forbid_list = [",", " "]
            for each_char in forbid_list:
                if each_char in self.account or each_char in self.password:
                    # print('账号密码不能含有逗号或空格')
                    self.login_fail('账号密码不能含有逗号或空格')
                    break
                else:
                    self.root.unbind("<KeyPress-Return>")
                    is_meet_demand = True
        else:
            self.login_fail("账号密码不能为空")
        return is_meet_demand

    def login(self, event=None):
        '''
        隐藏登录按钮和取消enter按键的绑定，防止用户不断点击登录而重复给服务器发信息
        '''
        # print("点击登录了")
        self.register_button.grid_forget()
        self.login_button.grid_forget()
        is_meet_demand = self.check_account_format()
        # print("账号密码是", self.account, self.password, is_meet_demand)
        if is_meet_demand:
            show_login_progress_thread = threading.Thread(target=self.show_login_progress)
            show_login_progress_thread.daemon = True
            show_login_progress_thread.start()
            # print("发送登录数据")
            if self.account == "hs" and self.password == "hs":
                self.login_success()
                self.HS_directory.write_user_info_file(self.account,
                                                       {"account": self.account, "password": self.password})
                self.HS_tool_GUI = HS_tool_app(self.root, self.account)
            else:
                self.q_sent.put([{"event": "login", "account": self.account, "password": self.password, "content_type":"text"}, ""])
                # self.q_sent.put([{"event": "login"},""])
        return is_meet_demand, self.account, self.password

    def register(self, event=None):
        print("点击注册按钮")
        is_meet_demand = self.check_account_format()
        if is_meet_demand:
            confirm = tk.messagebox.askyesno("Hi", f"确定用此账户{self.account}, 和密码{self.password}注册吗")
            if confirm:
                print("发送注册事件")
                self.q_sent.put(
                    [{"event": "register", "account": self.account, "password": self.password, "content_type": "text"},
                     ""])
            else:
                print("用户取消注册", confirm)

    def close(self):
        self.root.destroy()


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


class Login_app(Login_bind_event):
    def __init__(self, q_sent=None, q_recv=None, account="", password="", photo_path=""):
        super().__init__(q_sent, q_recv, account, password, photo_path)
        self.stop_handle_event = False
        self.handle_event_threading = threading.Thread(target=self.get_q)
        self.handle_event_threading.daemon = True
        self.handle_event_threading.start()
        self.root.mainloop()

    @add_event2dict("login")
    def login_result(self, data_dict, body):
        # print("登录结果是", data_dict, body)
        if "result" in data_dict:
            if data_dict["result"]:
                self.login_success()
                self.stop_handle_event = True
                if "account" in data_dict and "password" in data_dict:
                    self.account, self.password = data_dict["account"], data_dict["password"]
                self.HS_directory.write_user_info_file(self.account,
                                                       {"account": self.account, "password": self.password,
                                                        "cookie": data_dict["cookie"]})

                self.HS_tool_GUI = HS_tool_app(self.root, self.account,
                                               q_sent=self.q_sent, q_recv=self.q_recv,  cookie=data_dict["cookie"])
            else:
                self.login_fail(body)
        elif "error" in data_dict:
            self.login_fail(f'{data_dict["error"]}, {body}')

    @add_event2dict("register")
    def refister_result(self, data_dict=None, body=''):
        if body == "success":
            tk.messagebox.showinfo("hi", f"注册成功, 记得账户是{data_dict['account']}, 密码是{data_dict['password']}哦")
        else:
            tk.messagebox.showinfo("hi", f"注册失败, {body}")

    @add_event2dict("relogin")
    def relogin_result(self, data_dict=None, body=''):
        pass

    @add_event2dict("relogin_event")
    def relogin_event(self, data_dict=None, body=''):
        pass

    def get_q(self):
        while True:
            if not self.q_recv.empty():
                recv_data = self.q_recv.get()
                data_dict = recv_data[0]
                body = recv_data[1]
                # print("登陆界面收到事件返回数据", data_dict)
                if "event" in data_dict:
                    event = data_dict["event"]
                    event_dict[event](self, data_dict, body)
            if self.stop_handle_event:
                print("接收登录GUI获取事件")
                break
            time.sleep(0.01)

