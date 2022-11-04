import os
import socket
import json
import time
import traceback
import shutil
from multiprocessing import Process
# from multiprocessing import Queue
from abstract_client import  HS_socket, Client, get_current_ip
import socket

from tcp_protocol import MyProtocol
global_my_protocol_obj = MyProtocol()
from HS_universal.HS_directory import HS_directory
HS_directory_obj = HS_directory()


class Send_file_process(Process):
    def __init__(self, fileobj, header_dict, send_file_func, response_GUI_func):
        super().__init__()
        self.fileobj = fileobj
        self.header_dict = header_dict
        self.send_file_func = send_file_func
        self.response_GUI_func = response_GUI_func

    def run(self):
        print("我是发送文件进程", os.getpid())
        try:
            print("运行发送文件函数", self.header_dict)
            self.send_file_func(self.fileobj, self.header_dict, timeout=30)
            resond_dict, respond_body = global_my_protocol_obj.recv_data(self.fileobj, timeout=30)
            self.response_GUI_func(resond_dict, respond_body)
        except Exception as e:
            print("运行发送文件函数出错", str(e), os.getpid())
            traceback.print_exc()
            self.header_dict["error"] = "服务器响应信息错误"
            self.response_GUI_func(self.header_dict, "服务器响应错误、未响应或者已关闭")
        time.sleep(1)
        self.fileobj.close()


class Get_file_process(Process):
    def __init__(self, fileobj, header_dict, send_data_func, recv_data_func, response_GUI_func):
        super().__init__()
        self.fileobj = fileobj
        self.header_dict = header_dict
        self.send_data_func = send_data_func
        self.recv_data_func = recv_data_func
        self.response_GUI_func = response_GUI_func

    def run(self):
        # print("启动请求文件进程", os.getpid())
        try:
            print("运行请求文件函数")
            if self.header_dict["event"] == "get_avatar":
                print("发送获取头像请求++++++++++++++++++++++++++")
            self.send_data_func(self.fileobj, self.header_dict, '', timeout=30)
            respond_dict, body = self.recv_data_func(self.fileobj, timeout=30)
            if "event" in respond_dict:
                print("接收到文件", respond_dict)
                self.response_GUI_func(respond_dict, body)
            else:
                raise Exception("接收错误")
        except Exception as e:
            print("运行请求文件函数出错", str(e), os.getpid())
            traceback.print_exc()
            self.header_dict["error"] = "服务器响应信息错误"
            self.response_GUI_func(self.header_dict, "服务器响应错误、未响应或者已关闭")
        time.sleep(1)
        self.fileobj.close()



class HS_online_client(Client):
    def __init__(self, q_sent, q_recv):
        self.q_sent, self.q_recv = q_sent, q_recv
        # self.server_address = ("127.0.0.1", 7999)
        ip = get_current_ip()
        self.server_address = (ip, 7999)
        self.is_connect_ok = False
        self.am_i_running = True
        self.connect_server()
        self.tcp_protocol_obj = MyProtocol()

    def connect_server(self):
        try:
            self.HS_socket_obj = HS_socket(self.server_address)
            self.my_socket = self.HS_socket_obj.my_tcp_socket
            self.is_connect_ok = True
            # print("在线服务器连接成功")
        except Exception as e:
            self.is_connect_ok = False
            self.am_i_running = False
            # print("连接在线服务器失败", str(e))

    def re_connect_server(self):
        while True:
            try:
                self.HS_socket_obj = HS_socket(self.server_address)
                self.my_socket = self.HS_socket_obj.my_tcp_socket
                self.is_connect_ok = True
                break
            except Exception as e:
                self.am_i_running = False
                self.is_connect_ok = False
                # print("重新连接服务器失败", str(e))
                time.sleep(10)

    def get_file(self, header_dict):
        # print("开始请求文件", os.getpid())
        new_socket_obj = HS_socket(self.server_address)
        new_socket = new_socket_obj.my_tcp_socket
        send_file_process_obj = Get_file_process(new_socket, header_dict, self.tcp_protocol_obj.send_data,
                                                 self.tcp_protocol_obj.recv_data, self.response_GUI_event)
        send_file_process_obj.start()
        time.sleep(1)
        new_socket.close()

    def send_file(self, header_dict):
        # print("开始发送文件++++++++++++")
        new_socket_obj = HS_socket(self.server_address)
        new_socket = new_socket_obj.my_tcp_socket
        send_file_process_obj = Send_file_process(new_socket, header_dict, self.tcp_protocol_obj.send_file, self.response_GUI_event)
        send_file_process_obj.start()
        # print("发送文件进程已启动")
        time.sleep(1)
        new_socket.close()

    def handle_GUI_event(self, header_dict, body):
        if "event" in header_dict:  # 处理事件
            try:
                # print("处理GUI事件", header_dict, body)
                if (header_dict["event"] == "send_file" or header_dict["event"] == "change_my_avatar") and "file_path" in header_dict:
                    self.send_file(header_dict)
                elif header_dict["event"] == "get_file" or header_dict["event"] == "get_avatar":
                    self.get_file(header_dict)
                else:
                    print("发送事件")
                    self.tcp_protocol_obj.send_data(self.my_socket, header_dict, body, timeout=30)  # 尝试发送数据, 只能串行，因为服务器并行回复的话，数据可能会混乱
            except Exception as e:
                # print("处理GUI事件异常", str(e))
                traceback.print_exc()
                header_dict["error"] = "服务器故障"
                self.response_GUI_event(header_dict, "tcp 无法工作,连接服务器错误或者发送数据错误")
                time.sleep(1)

    def response_GUI_event(self, header_dict, body):
        # print("回复GUI事件", header_dict, body)
        self.q_sent.put([header_dict, body])

    def get_server_event(self, my_socket):
        header_dict, body = self.tcp_protocol_obj.recv_data(my_socket)  #, timeout=120)
        print("收到服务器事件", header_dict, body)
        self.handle_server_event(header_dict, body)

    def handle_server_event(self, header_dict, body):
        self.response_GUI_event(header_dict, body)

    def start_work(self):
        '''
        接口/运行函数
        '''
        self.am_i_running = True
        while True:
            try:
                # print("我在接收服务器事件")
                self.get_server_event(self.my_socket)
            except Exception as e:
                # print("获取服务器数据失败", str(e))
                if "socket closed" in str(e) or not self.is_connect_ok:
                    if self.am_i_running:
                        self.am_i_running = False
                        # print("改为离线处理")
                        self.re_connect_server()  # 阻塞，只有重连成功才会往下一步执行
                        # print("改回在线处理")
                        self.am_i_running = True
                        # print("通知GUI重新登录")
                        self.response_GUI_event({"event": "relogin_event", "error": "服务器故障", "data_type": "text"},
                                        "tcp 无法工作,连接服务器错误或者发送数据错误")

    def stop_work(self): pass










