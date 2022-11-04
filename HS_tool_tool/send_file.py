import os
import sys
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
from multiprocessing import Queue

import my_tcp
from haimeng_tk import *

class SendFile:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("文件传输")
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.help_frame = tk.Frame(self.root)
        self.help_frame.pack(fill="x")
        self.ip_frame = tk.Frame(self.root)
        self.ip_frame.pack(fill="x", padx=30)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill="x", padx=30)
        help_str=(
            "使用说明：\n"
            "  1. 接收方填写我的IP和端口, 点击bind, 亮绿灯绑定成功\n"
            "  2. 发送方填写对方IP和端口(即接收方在第1步填写的), 点击connect, 亮绿灯连接成功\n"
            "  3. 发送方点击send file, 接收方选择保存位置进行接收"
        )

        tk.Label(self.help_frame, text=help_str, justify="left", fg=color_change(20, 50, 30))\
            .grid(row=0, column=0, sticky="w", pady=10)
        tk.Label(self.ip_frame, text="我的IP").grid(row=0, column=0)
        tk.Label(self.ip_frame, text="对方IP").grid(row=1, column=0)
        tk.Label(self.ip_frame, text="端口").grid(row=0, column=2)
        tk.Label(self.ip_frame, text="端口").grid(row=1, column=2)
        self.my_ip_entry = tk.Entry(self.ip_frame)
        self.my_ip_entry.grid(row=0, column=1)
        self.recv_ip_entry = tk.Entry(self.ip_frame)
        self.recv_ip_entry.grid(row=1, column=1)
        self.my_port_entry = tk.Entry(self.ip_frame, width=4)
        self.my_port_entry.grid(row=0, column=3)
        self.recv_port_entry = tk.Entry(self.ip_frame, width=4)
        self.recv_port_entry.grid(row=1, column=3)

        self.is_connect_ft = tkFont.Font(family='黑体', size=20)  # 第一列我的名字字体
        self.bind_button = tk.Button(self.ip_frame, text="bind", fg="blue", width=8)
        self.bind_button.grid(row=0, column=4, padx=5)
        self.is_bind_label = tk.Label(self.ip_frame, text="♼", font=self.is_connect_ft, fg="gray")
        self.is_bind_label.grid(row=0, column=5)
        self.connect_button = tk.Button(self.ip_frame, text="connect", fg="blue", width=8)
        self.connect_button.grid(row=1, column=4, padx=5)
        self.is_connect_label = tk.Label(self.ip_frame, text="♼", font=self.is_connect_ft, fg="gray")
        self.is_connect_label.grid(row=1, column=5)

        self.send_file_button = tk.Button(self.button_frame, text="send file", fg="blue")
        self.send_file_button.grid(row=0, column=2, sticky="w", padx=5, pady=10)
        self.send_folder_button = tk.Button(self.button_frame, text="send folder", fg="blue")
        self.send_folder_button.grid(row=0, column=3, sticky="w", padx=5, pady=10)
        self.log_label = tk.Label(self.button_frame, text="")
        self.log_label.grid(row=0, column=4, sticky="w", padx=5, pady=10)


class SendFileApp(SendFile):
    def __init__(self):
        super().__init__()
        self.bind_button["command"] = self.bind_ip
        self.connect_button["command"] = self.connect_server
        self.send_file_button["command"] = self.send_file
        self.send_folder_button["command"] = self.send_folder
        self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)
        self.root.resizable(0, 0)
        self.my_client, self.my_server = None, None
        self.my_ip = my_tcp.get_current_ip()
        self.my_port = 8888
        self.my_ip_entry.insert(0, self.my_ip)
        self.my_port_entry.insert(0, str(self.my_port))
        self.bind_ip()

        self.recv_port_entry.insert(0, self.my_port)
        self.root.mainloop()

    @staticmethod
    def check_ip_format(IP):
        # 192.168.0.1, 10.56.24.8
        if not IP or re.search("(\d{0,3}.){3}.\d{0,3}", IP) is None:
            return False
        return True

    def handle_client(self, client_socket, client_address):
        print("启动多线程等待客户端数据")
        recv_data_info, recv_data = my_tcp.receive_data(client_socket)  # 阻塞接收
        print("收到数据", recv_data_info, recv_data)
        if "send file" == recv_data_info["event"]:
            q = Queue()
            save_dir = tkfile.askdirectory(title="请选择保存位置")
            if save_dir:
                recv_data_info["save_dir"] = save_dir
                my_tcp.start_recv_files(recv_data_info, client_socket, q=q)
                threading.Thread(target=self.detect_file_progress, args=("接收进度", q,)).start()

    def recv_client(self):
        while True:
            try:
                print("开始倾听客户端")
                client_socket, client_address = self.my_server.receive_client()  # 阻塞接收
                self.log_label["text"] = f"收到客户端{client_address}连接"
                handle_client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, client_address,))
                handle_client_thread.setDaemon(True)
                handle_client_thread.start()
            except Exception as e:
                print("服务器倾听客户端异常", str(e))
                break
            sleep(0.05)

    def bind_ip(self):
        print("开始绑定地址")
        ip = self.my_ip_entry.get()
        port = self.my_port_entry.get()
        if not self.check_ip_format(ip) or not str(port).isdigit():
            self.is_bind_label["fg"] = "gray"
            # tkmessage.showerror("", f"ip或者端口格式不正确{ip,port}")
            self.log_label["text"] = f"ip或者端口格式不正确{ip,port}"
        else:
            try:
                print("关闭服务器")
                if self.my_server is not None:
                    self.my_server.my_tcp_socket.close()
            except Exception as e:
                print("关闭服务器失败", str(e))

            try:
                print("绑定新地址")
                self.my_server = my_tcp.MyServer(ip, int(port))
                self.is_bind_label["fg"] = color_change(120, 248, 90)
                self.handle_client_thread = threading.Thread(target=self.recv_client)
                self.handle_client_thread.daemon = True
                self.handle_client_thread.start()
            except Exception as e:
                self.is_bind_label["fg"] = "red"
                self.log_label["text"] = str(e)

    def real_connect_server(self, ip, port):
        my_client = my_tcp.MyClient((ip, int(port)), False)
        if not my_client.connect_server((ip, int(port))):
            self.is_connect_label["fg"] = "red"
            self.log_label["text"] = f"连接{ip, port}失败"
        else:
            print("连接成功")
            self.is_connect_label["fg"] = color_change(120, 248, 90)
            return my_client

    def connect_server(self):
        ip = self.recv_ip_entry.get()
        port = self.recv_port_entry.get()
        if not self.check_ip_format(ip) or not str(port).isdigit():
            self.is_bind_label["fg"] = "gray"
            # tkmessage.showerror("", f"ip或者端口格式不正确{ip,port}")
            self.log_label["text"] = f"ip或者端口格式不正确{ip, port}"
        else:
            my_client = self.real_connect_server(ip, port)
            return my_client

    def detect_file_progress(self, file_name, q, **kwargs):
        while True:
            if not q.empty():
                q_data = q.get()
                if "float" in str(type(q_data)) or "int" in str(type(q_data)):
                    self.log_label["text"] = f"{file_name}: {q_data:.2%}"
                if q_data == 1:
                    if "is_recv" not in kwargs:
                        break
                if "is_recv" in kwargs:  # 等待文件解压
                    if "fist_file_name" in str(q_data):
                        break
            sleep(0.05)

    def get_file_name(self, file_path):
        if "tuple" in str(type(file_path)) or "list" in str(type(file_path)):
            file_name = os.path.basename(file_path[0])
        else:
            file_name = os.path.basename(file_path)
        return file_name

    def send_file_directory(self, file_path, client):
        data_info = {}
        data_info["file_path"] = file_path
        q = Queue()
        my_tcp.start_send_files(data_info, client, is_delete_file=False, q=q)
        file_name = self.get_file_name(file_path)
        threading.Thread(target=self.detect_file_progress, args=(os.path.basename(file_name), q, )).start()

    def send_file(self):
        my_client = self.connect_server()
        if not my_client.is_connect_ok:
            self.log_label["text"] = "尚未连接成功"
        else:
            file_path = tkfile.askopenfilenames(title="choose files to send")
            if len(file_path) > 0:
                self.send_file_directory(file_path, my_client.my_tcp_socket)


    def send_folder(self):
        my_client = self.connect_server()
        if not my_client.is_connect_ok:
            self.log_label["text"] = "尚未连接成功"
        else:
            directory = tkfile.askdirectory(title="chose a directory to send")
            if directory:
                self.send_file_directory(directory, my_client.my_tcp_socket)

    def close_GUI(self):
        if self.my_server is not None:
            try:
                self.my_server.close()
                print("关闭文件传输服务器")
            except:
                pass
        self.root.destroy()
