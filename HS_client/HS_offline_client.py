import os
import socket
import json
import time
import traceback
import shutil
from multiprocessing import Process
# from multiprocessing import Queue
import threading
import subprocess
import platform
import re
import socket

from abstract_client import  HS_socket, Client, get_current_ip
from tcp_protocol import MyProtocol
from HS_universal.HS_directory import HS_directory
HS_directory_obj = HS_directory()


event_fun_dict = {}
global_internal_server_port = 6666
global_my_account = ''
global_tcp_protocol_obj = MyProtocol()
def add_event2dict(event_name):
    '''
    将事件名和对应函数名添加到字典的装饰器
    '''
    def set_fun(fun):
        global event_fun_dict
        event_fun_dict[event_name] = fun  # 这一步只有装饰的时候才会被调用
        def call_fun(*args, **kwargs):
            return fun(*args, **kwargs)
        return call_fun
    return set_fun


def check_data_dict(key_list):
    '''
    将事件名和对应函数名添加到字典的装饰器
    '''
    def set_fun(fun):
        def call_fun(*args, **kwargs):
            # print("开始检测data_dict", key_list)
            for each_key in key_list:
                # print("正在检测", each_key)
                if each_key not in args[0]:
                    if "event" in args[0]:
                        return {"event":args[0]["event"], "error": f"parameter error, need {each_key}"},  ""
                    else:
                        return {}, ""
            return fun(*args, **kwargs)
        return call_fun
    return set_fun

        
class InternalServer:
    def __init__(self, q_sent):
        # print("开启内部服务器")
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许地址复用， 防止关闭程序后此连接还在，重新打开程序报地址已被连接的错误
        self.ip = get_current_ip()
        # self.ip='127.0.0.1'
        port = global_internal_server_port
        try:
            self.server_socket.bind((self.ip, port))
            self.server_socket.listen(128)
        except Exception as e:
            # print("绑定地址失败", str(e))
            self.kill_port_process(global_internal_server_port)
        self.q_sent = q_sent
        self.tcp_protocol_obj = MyProtocol()

    def kill_port_process(self, port):
        if platform.system() == "Darwin":
            # print("开始写入----------------")
            command_out_path = os.path.join(HS_directory_obj.File, "command_result.txt")
            f = open(command_out_path, "w")
            subprocess.run(f"lsof -i tcp:{port}", shell=True, stdout=f)
            f.close()
            f = open(command_out_path, "r")
            result = f.read()
            # print("端口结果是---------", result, "\n\n")
            pid_port_re = re.search(r"[^\d]+?(\d{1,5})[^\d]*?.*?" + str(port), result)
            # print("--------------", pid_port_re)
            if pid_port_re is not None:
                # print("+++++++++pid是+++++++++", pid_port_re.group(1))
                pid = int(pid_port_re.group(1))
                f = open(command_out_path, "w")
                subprocess.run(f"kill -9 {pid}", shell=True, stdout=f)
                f.close()
                # print("已经杀死端口", pid)
                time.sleep(2)
                self.server_socket.bind((self.ip, port))
                self.server_socket.listen(128)
                # print("+++++++++绑定地址成功+++++++++++")
            else:
                print("+++++++++找不到pid+++++++++++， 杀端口失败")

    def accept(self):
        while True:
            try:
                # print("内部服务器等待接收连接")
                client_socket, client_address = self.server_socket.accept()
                # print("内部服务器收到连接")
                handle_client_t = threading.Thread(target=self.handle_client, args=(client_socket, client_address, ))
                handle_client_t.start()
            except:
                break

    def handle_client(self, client_socket, client_address):
        try:
            header_dict, body = self.tcp_protocol_obj.recv_data(client_socket, 120)
            print("内部服务器收到数据", header_dict, body)
            respond_GUI_dict = {}
            respond_GUI_dict.update(header_dict)
            respond_GUI_body = body
            if header_dict["event"] == "send_message":
                print("内部服务器发送消息", body)
                respond_GUI_dict["event"] = "recv_message"
                respond_GUI_dict["time"] = ""
                self.response_GUI_event(respond_GUI_dict, respond_GUI_body)  # 通知GUI收到消息
            if header_dict["event"] == "send_file":
                respond_GUI_dict["event"] = "recv_file"
                respond_GUI_dict["time"] = ""
                self.response_GUI_event(respond_GUI_dict, respond_GUI_body)
                header_dict["content_type"] = "text"
            if header_dict["event"] == "search_friend":
                my_account = search_my_account(header_dict["cookie"])
                if my_account:
                    respond_GUI_body = str(((my_account, ""),))
                    header_dict["content_type"] = "eval"
            if header_dict["event"] == "get_friend_info":
                my_info_dict = search_my_info(header_dict["cookie"])
                ip = get_current_ip()
                myinfo = (my_info_dict["account"], my_info_dict["name"], my_info_dict["sign"], my_info_dict["photo"],
                          b'\x01', my_info_dict["birthday"], my_info_dict["gender"], my_info_dict["address"],
                          my_info_dict["phone"], my_info_dict["mail"], ip, "", "",)
                respond_GUI_body = str(myinfo)
                header_dict["content_type"] = "eval"
            self.tcp_protocol_obj.send_data(client_socket, header_dict, respond_GUI_body, 30)  # 通知对方数据已经被接收
            client_socket.close()
        except Exception as e:
            print("接收数据出错", str(e))
            client_socket.close()

    def response_GUI_event(self, header_dict, body):
        # print("回复GUI事件", header_dict, body)
        self.q_sent.put([header_dict, body])


@add_event2dict("login")  # 相当于 @setfun
@check_data_dict(["account", "password"])
def login(header_dict, body, *args):
    # print("处理登录事件+++++++++")
    user_info_dict = HS_directory_obj.read_user_info_file(header_dict["account"])
    if user_info_dict:
        # print("用户是", user_info_dict)
        if user_info_dict["password"] == header_dict["password"]:
            header_dict["result"] = True
            header_dict["cookie"] = user_info_dict["cookie"]
            global global_my_account
            global_my_account = header_dict["account"]
            return header_dict, ""
        else:
            header_dict["result"] = False
            return header_dict, "密码不正确"
    else:
        header_dict["result"] = False
        return header_dict, "未找到用户"

def search_my_info(cookie):
    # print("搜索我的账户", cookie)
    global global_my_account
    for each_file in os.listdir(HS_directory_obj.config_dir):
        if each_file=="current_user":
            try:
                # print("搜索", each_file)
                user_info = HS_directory_obj.read_user_info_file(each_file)
                # print("搜索结果", user_info, cookie)
                if user_info and user_info["cookie"] == cookie:
                    global_my_account = user_info["account"]
                    return user_info
            except:
                return {}
    return {}


def search_my_account(cookie):
    # print("搜索我的账户", cookie)
    for each_file in os.listdir(HS_directory_obj.config_dir):
        if each_file=="current_user":
            try:
                print("搜索", each_file)
                user_info = HS_directory_obj.read_user_info_file(each_file)
                print("搜索结果", user_info, cookie)
                if user_info and user_info["cookie"] == cookie:
                    return user_info["account"]
            except:
                return ""
    return ""



def search_ip(cookie, target_account):
    global global_my_account
    target_ip = ""
    if not global_my_account:
        global_my_account = search_my_account(cookie)
    if global_my_account:
        target_user = HS_directory_obj.read_user_info_file(global_my_account)
        print("对方是", target_user)
        target_ip = target_user["friend_dict"][target_account]["ip"]
    return target_ip


@add_event2dict("send_message")
@check_data_dict(["cookie", "target_account"])
def send_message(header_dict, body, *args):
    target_ip = search_ip(header_dict["cookie"], header_dict["target_account"])
    print("对方ip", target_ip)
    if target_ip:
        new_socket_obj = HS_socket((target_ip, global_internal_server_port))
        new_socket = new_socket_obj.my_tcp_socket
        header_dict["from_account"] = global_my_account
        global_tcp_protocol_obj.send_data(new_socket, header_dict, body, timeout=10)  # 尝试发送数据, 只能串行，因为服务器并行回复的
        time.sleep(0.5)
        try:
            global_tcp_protocol_obj.recv_data(new_socket, timeout=10)
            new_socket.close()
        except:
            new_socket.close()
        return header_dict, "success"
    else:
        return header_dict, "failed"

@add_event2dict("search_friend")
@check_data_dict(["cookie"])
def search_friend(header_dict, body, *args):
    print("搜索好友", body)
    target_ip = body
    new_socket_obj = HS_socket((target_ip, global_internal_server_port))
    new_socket = new_socket_obj.my_tcp_socket
    global global_my_account
    if not global_my_account:
        global_my_account = search_my_account(header_dict["cookie"])
    header_dict["from_account"] = global_my_account
    global_tcp_protocol_obj.send_data(new_socket, header_dict, body, timeout=10)  # 尝试发送数据, 只能串行，因为服务器并行回复的
    time.sleep(0.5)
    respond_body = "success"
    try:
        respond_dict, respond_body = global_tcp_protocol_obj.recv_data(new_socket, timeout=10)
        print("回复搜索结果给GUI", respond_dict, respond_body )
        new_socket.close()
    except:
        new_socket.close()
    return header_dict, respond_body


@add_event2dict("add_new_friend")
@check_data_dict(["cookie"])
def add_new_friend(header_dict, body, *args):
    # [account, name, sign, photo, is_online, birthday, gender, address, phone, mail, ip, nickname, time]
    my_info_dict = search_my_info(header_dict["cookie"])
    if my_info_dict:
        ip =get_current_ip()
        myinfo = ((my_info_dict["account"], my_info_dict["name"], my_info_dict["sign"], my_info_dict["photo"],
                   b'\x01', my_info_dict["birthday"], my_info_dict["gender"], my_info_dict["address"], my_info_dict["phone"], my_info_dict["mail"],
                   ip, "", "",
                   ), )
        header_dict["result"] = str(myinfo)
        header_dict["content_type"] = "eval"
        return header_dict, "success"
    else:
        return header_dict, "failed"


@add_event2dict("get_friend_info")
@check_data_dict(["cookie"])
def get_friend_info(header_dict, body, *args):
    my_info_dict = search_my_info(header_dict["cookie"])
    if my_info_dict:
        friend_list = []
        print("=============", my_info_dict["friend_dict"])
        for each_friend in my_info_dict["friend_dict"]:
            new_socket = None
            friend_info_dict = my_info_dict["friend_dict"][each_friend]
            try:
                target_ip = friend_info_dict["ip"]
                new_socket_obj = HS_socket((target_ip, global_internal_server_port))
                new_socket = new_socket_obj.my_tcp_socket
                header_dict["from_account"] = global_my_account
                global_tcp_protocol_obj.send_data(new_socket, header_dict, body, timeout=10)  # 尝试发送数据, 只能串行，因为服务器并行回复的
                time.sleep(0.5)
                respond_dict, respond_body = global_tcp_protocol_obj.recv_data(new_socket, timeout=10)
                print("好友信息是", respond_dict, respond_body)
                if respond_body:
                    friend_list.append(respond_body)
                else:
                    friend_info = (
                        friend_info_dict["account"], friend_info_dict["name"], friend_info_dict["sign"], friend_info_dict["photo"],
                        b'\x00', friend_info_dict["birthday"], friend_info_dict["gender"], friend_info_dict["address"],
                        friend_info_dict["phone"], friend_info_dict["mail"], "", "", "",
                     )
                    friend_list.append(friend_info)
                new_socket.close()
            except:
                if new_socket is not None:
                    new_socket.close()
                friend_info = (
                    friend_info_dict["account"], friend_info_dict["name"], friend_info_dict["sign"], friend_info_dict["photo"],
                    b'\x00', friend_info_dict["birthday"], friend_info_dict["gender"], friend_info_dict["address"],
                    friend_info_dict["phone"], friend_info_dict["mail"], "", "", "",
                )
                friend_list.append(friend_info)
        header_dict["content_type"] = "eval"
        print("最终好友信息", friend_list)
        return header_dict, tuple(friend_list)



class Send_file_process(Process):
    def __init__(self, fileobj, header_dict, response_GUI_func):
        super().__init__()
        self.fileobj = fileobj
        self.header_dict = header_dict
        self.response_GUI_func = response_GUI_func

    def run(self):
        # print("我是发送文件进程", os.getpid())
        try:
            # print("运行发送文件函数", self.header_dict)
            global_tcp_protocol_obj.send_file(self.fileobj, self.header_dict, timeout=30)
            global_tcp_protocol_obj.recv_data(self.fileobj, timeout=30)
            self.response_GUI_func(self.header_dict, "success")
        except Exception as e:
            # print("运行发送文件函数出错", str(e), os.getpid())
            traceback.print_exc()
            self.header_dict["error"] = "服务器响应信息错误"
            self.response_GUI_func(self.header_dict, "服务器响应错误、未响应或者已关闭")
        time.sleep(1)
        self.fileobj.close()


@add_event2dict("send_file")
@check_data_dict(["cookie", "target_account"])
def send_file(header_dict, body, *args):
    target_ip = search_ip(header_dict["cookie"], header_dict["target_account"])
    if target_ip:
        print("发送文件给", target_ip)
        header_dict["from_account"] = global_my_account
        new_socket_obj = HS_socket((target_ip, global_internal_server_port))
        new_socket = new_socket_obj.my_tcp_socket
        send_file_process_obj = Send_file_process(new_socket, header_dict,  args[0])
        send_file_process_obj.start()
        time.sleep(0.5)
        new_socket.close()
        return {}, "success"


@add_event2dict("get_file")
@check_data_dict(["cookie", "target_account"])
def send_file(header_dict, body, *args):
    return header_dict, "success"



class HS_offline_client(Client):
    def __init__(self, q_sent, q_recv):
        '''
        ip_dict获取方法？？
        '''
        self.q_sent, self.q_recv = q_sent, q_recv
        self.server_address = ("", global_internal_server_port)
        self.tcp_protocol_obj = MyProtocol()
        self.ip_dict = {"haimeng_lan": "10.54.200.117"}
        self.internal_server_obj = InternalServer(self.q_sent)
        self.am_i_running = False

    def connect_server(self):
        try:
            self.HS_socket_obj = HS_socket(self.server_address)
            self.my_socket = self.HS_socket_obj.my_tcp_socket
        except Exception as e:
            print("连接服务器失败", str(e))

    def handle_GUI_event(self, header_dict, body):
        '''
        只支持发送消息和文件！
        和通过IP搜索好友（IP信息保存在本地中，只会增加，不会减少，默认保存数据库里的全部IP, 一旦登录就获取全部IP, 并且保存好友列表）
        '''
        if "event" in header_dict:  # 处理事件
            try:
                if "event" in header_dict and header_dict["event"] in event_fun_dict:
                    print("离线处理GUI事件", header_dict, event_fun_dict)
                    respond_dict, respond_body = event_fun_dict[header_dict["event"]](header_dict, body, self.response_GUI_event)
                    print("处理结果", respond_dict, respond_body)
                    if respond_dict:
                        self.response_GUI_event(respond_dict, respond_body)
            except Exception as e:
                print("处理GUI事件异常", str(e))
                traceback.print_exc()
                header_dict["error"] = "对方不在线"
                self.response_GUI_event(header_dict, "请等待对方在线重试")
                time.sleep(1)


    def response_GUI_event(self, header_dict, body):
        # print("回复GUI事件", header_dict, body)
        self.q_sent.put([header_dict, body])

    def start_work(self):
        '''
        接口/运行函数
        '''
        self.am_i_running = True
        start_internal_server = threading.Thread(target=self.internal_server_obj.accept, args=())
        start_internal_server.daemon = True
        start_internal_server.start()


    def stop_work(self):
        self.internal_server_obj.server_socket.setblocking(False)
        self.am_i_running = False