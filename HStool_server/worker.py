import time
import json
import time
import socket
import threading
import uuid
from sqler import HS_mysql
import traceback
from multiprocessing import Lock, Process
import os
import sys
import platform

import haimeng_time
from haimeng_time import changelocaltimeToSqldatetime
from HS_directory import HS_directory
from tcp_protocol import MyProtocol

event_fun_dict = {}
global_fd_dict = {}
global_thread_send = []
global_thread_recv = []
global_send_condition = threading.Condition()
global_recv_condition = threading.Condition()
HS_directory_obj = HS_directory()
global_protocol_obj = MyProtocol()

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
                if each_key not in args[1]:
                    if "event" in args[1]:
                        return {"event":args[1]["event"], "error": f"parameter error, need {each_key}"},  "",  ""
                    else:
                        return {}, "", ""
            return fun(*args, **kwargs)
        return call_fun
    return set_fun


def search_account_by_(account="", cookie="", field_list=["*"], sqlConn=None):
    if sqlConn is None:
        sqlConn = HS_mysql()
    if account:
        result = sqlConn.search("Contact", field_list, "where account=%s", [account])
    else:
        result = sqlConn.search("Contact", field_list, "where cookie=%s", [cookie])
    if is_close:
        sqlConn.close()
    # print("该用户是", result)
    return result

def search_account_by(search_dict, field_list=["*"], sqlConn=None):
    is_close = False
    if sqlConn is None:
        is_close = True
        sqlConn = HS_mysql()
    result = tuple()
    for key in search_dict:
        result = sqlConn.search("Contact", field_list, f"where {key}=%s", [search_dict[key]])
        break
    if is_close:
        sqlConn.close()
    return result


def inform_user_info_change(owner_account):
    # 查找此用户在线好友，然后一个个发出通知
    print(f"通知用户{owner_account}好友")
    sqlConn = HS_mysql()
    owner = search_account_by({"account":owner_account}, ["account", "name", "sign", "photo", "is_online",
                                                    "birthday", "gender", "address", "phone", "mail", "ip"], sqlConn)

    result = sqlConn.inner_join_search("Contact", ["account", "name", "sign", "photo", "is_online",
                                                    "birthday", "gender", "address", "phone", "mail", "fd_file",],
                                        "relationship", ["nickname", "time"],
        f"on relationship.friend_account='{owner_account}' and Contact.is_online=b'1' and relationship.owner_account=Contact.account order by relationship.time desc")
    sqlConn.close()
    print('用户的在线好友是', result)
    # 用户的在线好友是(('Haimeng_Lan', '蓝海梦', '人生得意须尽欢', 'Haimeng_Lan1650362048.png', b'\x01', '1993-11-23', '男', '广西南宁市',
    #       '151 5149 3718', 'Haimeng_Lan@luxshare-ict.com','fd', '', datetime.datetime(2022, 4, 20, 12, 34, 51)), )
    if result:
        for each_friend in result:
            if each_friend and each_friend[0]!=owner_account:
                respond_dict = {"event":"user_info_change", "from_account": owner_account}
                respond_body = owner[0]
                print(f"发送给用户好友", respond_dict, respond_body)
                sent_result(fd=each_friend[10], data_dict=respond_dict, body=respond_body, data_type="eval")


@add_event2dict("login")  # 相当于 @setfun
@check_data_dict(["account", "password"])
def login(fd,  data_dict, body, *args):
    # todo 登录正确, 修改用户在线状态以及cookie, fd信息
    # print("收到登录请求", data_dict)
    response_dict = {}
    response_body = ""
    response_dict.update(data_dict)
    user = search_account_by({"account":data_dict["account"]}, field_list=["account", "password",  "is_online"])
    print("该用户是", user)
    if user and user[0][0] == data_dict["account"] and user[0][1] == data_dict["password"]:
        response_dict["result"] = True
        response_dict["cookie"] = str(uuid.uuid1())
        response_dict["content_type"] = "text"
        response_dict["result"] = True
        sqlConn = HS_mysql()
        # print("+++++++++++++++++++++++++保存用户登录信息+++++++++++", fd)
        address = global_fd_dict[fd].getpeername()
        ip = address[0]
        sqlConn.modify("Contact", {"fd_file": fd, "cookie": response_dict["cookie"], "is_online": b"1", 
                       "connect_time": changelocaltimeToSqldatetime(), "ip":ip},
                       "where account=%s", params=[data_dict['account']])
        inform_user_info_change(user[0][0])
        if user[0][2]==b'\x01':
            try:
                response_dict["event"] = "login_in_other_place"
                response_body = "someone try to login in other place"
                global_protocol_obj.send_data(global_fd_dict[user[0][3]], response_dict, str(response_body), 1)
                clear_user_status(fd=user[0][3])
                response_body = "此用户已登录，已令其下线，请重登"
            except:
                pass
        response_dict["event"] = "login"
    else:
        response_body = "账号密码错误"
        response_dict["result"] = False
    response_dict["content_length"] = 0
    return response_dict, response_body, ''


@add_event2dict("register")  # 相当于 @setfun
@check_data_dict(["account", "password"])
def register(fd,  data_dict, body, *args):
    # todo 登录正确, 修改用户在线状态以及cookie, fd信息
    print("收到注册请求", data_dict)
    response_dict = {}
    response_dict.update(data_dict)
    sqlConn = HS_mysql()
    user = search_account_by({"account":data_dict["account"]}, sqlConn=sqlConn)
    if user:
        sqlConn.close()
        return response_dict, "此账号已被别人注册过啦", "text"
    else:
        address = global_fd_dict[fd].getpeername()
        ip = address[0]
        print("用户ip是", ip)
        user = search_account_by({"ip": ip})
        if user:
            sqlConn.close()
            return response_dict, "此ip已被注册过啦", "text"
        else:
            sqlConn.add("Contact", {"account": data_dict["account"], "password": data_dict["password"]})
            return response_dict, "success", "text"


@add_event2dict("relogin")
@check_data_dict(["cookie"])
def relogin(fd,  data_dict, body, *args):
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"], sqlConn=sqlConn)
    if user and user[0]:
        data_dict["cookie"] = str(uuid.uuid1())
        sqlConn.modify("Contact", {"fd_file": fd, "cookie": data_dict["cookie"], "is_online": b"1"},
                       "where account=%s", params=[user[0][0]])
        # print(f"用户{user[0][0]}重新登录成功，fd改为{fd}")
        data_dict["content_length"] = len("success".encode())
        sqlConn.close()
        data_dict["result"] = True
        return data_dict, '', ''
    else:
        sqlConn.close()
        data_dict["result"] = False
        return data_dict, '', ''


def clear_user_status(fd=None, account=None):
    sqlConn = HS_mysql()
    if fd is not None:
        user = search_account_by({"fd_file": fd}, field_list=["account"])
        print(f"用户{user}退出了")
        sqlConn.modify("Contact", {"is_online": b"0", "fd_file": 0}, "where fd_file=%s", params=[fd])
        if user:
            inform_user_info_change(user[0][0])
    elif account is not None:
        sqlConn.modify("Contact", {"is_online": b"0", "fd_file": 0}, "where account=%s", params=[account])
        inform_user_info_change(account)
    if fd is None and account is None:
        sqlConn.modify("Contact", {"is_online": b"0", "fd_file": 0}, "where is_online=%s", params=[b"1"])
    # print(f"修改用户状态成功")
    sqlConn.close()


@add_event2dict("get_my_info")
@check_data_dict(["cookie"])
def get_my_info(fd,  data_dict, body, *args):
    result = search_account_by({"cookie":data_dict["cookie"]}, field_list=["name", "sign", "photo", "birthday", "gender", 
                                "address", "phone", "mail"])
    return data_dict, result, "eval"


@add_event2dict("get_friend_info")
@check_data_dict(["cookie"])
def get_friend_info(fd,  data_dict, body, *args):
    '''
    command = select c.account,c.photo, c.sign, r.nickname from contact as c inner join relationship as r on
              r.friend_account in ("Chao_Jiang", "Haimeng_Lan") and c.account=r.friend_account and
              r.owner_account="Haimeng_Lan" and c.is_online=b'1' order by r.time desc limit 0,100;
    '''
    # print("++++++++++++++++请求获取好友信息+++++++++++++++", data_dict)
    if "cookie" in data_dict:
        '''
        按顺序返回account, name, sign, photo, is_online,
                            birthday, gender, address, phone, mail,nickname, time
        '''
        sqlConn = HS_mysql()
        # result = sqlConn.search("Contact", ["*"], "")
        account = search_account_by({"cookie":data_dict["cookie"]}, sqlConn=sqlConn)
        print("账户是", account)
        if account:
            owner_account = account[0][1]
            result = sqlConn.inner_join_search("Contact", ["account", "name", "sign", "photo", "is_online",
                                                           "birthday", "gender", "address", "phone", "mail", 'ip'],
                                               "relationship", ["nickname", "time"],
                                               f"on relationship.owner_account='{owner_account}' and relationship.friend_account=Contact.account order by relationship.time desc")
            sqlConn.close()
            print("返回好友信息", data_dict, result)
            return data_dict, result, "eval"
    sqlConn.close()
    return {}, "", ""


@add_event2dict("modify_my_info")
@check_data_dict(["cookie", "from_account", "modify_dict"])
def modify_my_info(fd,  data_dict, body, *args):
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]},  field_list=["account"], sqlConn=sqlConn)
    if user and user[0][0]==data_dict["from_account"]:
        sqlConn.modify("Contact", data_dict["modify_dict"], "where account=%s", params=[user[0][0]])
        sqlConn.close()
        print("修改我的信息成功")
        return data_dict, "success", "text"
    else:
        sqlConn.close()
        return data_dict, "failed", "text"


@add_event2dict("modify_friend_info")
@check_data_dict(["cookie", "target_account", "modify_dict"])
def modify_friend_info(fd,  data_dict, body, *args):
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]},  field_list=["account"], sqlConn=sqlConn)
    if user:
        sqlConn.modify("relationship", data_dict["modify_dict"], "where owner_account=%s and friend_account=%s", 
            params=[user[0][0], data_dict["target_account"]])
        print("修改好友备注成功")
        sqlConn.close()
        return data_dict, "success", "text"
    else:
        sqlConn.close()
        return data_dict, "failed", "text"



@add_event2dict("delete_friend")
@check_data_dict(["cookie", "target_account"])
def delete_friend(fd,  data_dict, body, *args):
    # print("收到删除好友请求")
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"], sqlConn=sqlConn)
    if user and user[0]:
        sqlConn.delete("relationship", "where friend_account=%s and owner_account=%s",
                       [data_dict["target_account"], user[0][0]])
        sqlConn.close()
        return data_dict, "success", "text"
    else:
        sqlConn.close()
        return data_dict, "failed", "text"


@add_event2dict("add_new_friend")
@check_data_dict(["cookie", "target_account"])
def add_new_friend(fd,  data_dict, body, *args):
    # print("收到添加好友请求")
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"], sqlConn=sqlConn)
    if user and user[0]:
        sqlConn.add("relationship", {"owner_account": user[0][0], "friend_account": data_dict["target_account"]})
        result = sqlConn.inner_join_search("Contact", ["account", "name", "sign", "photo", "is_online",
                                                       "birthday", "gender", "address", "phone", "mail", "ip"],
                                           "relationship", ["nickname", "time"],
                                           f"on relationship.owner_account='{user[0][0]}' and relationship.friend_account='{data_dict['target_account']}' and relationship.friend_account=Contact.account")
        print("添加的好友是", result)
        data_dict["result"] = str(result)
        sqlConn.close()
        return data_dict, "success", "text"
    else:
        return data_dict, "failed", "text"

        return data_dict, "failed", "text"


@add_event2dict("search_friend")
@check_data_dict(["cookie"])
def search_friend(fd,  data_dict, body, *args):
    # print("收到添加好友请求")
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"], sqlConn=sqlConn)
    if user and user[0]:
        result = sqlConn.search("Contact", ["account", "name"], "where account like %s", params=[f'%{body}%'])
        sqlConn.close()
        return data_dict, result, "eval"
    else:
        return data_dict, "failed", "eval"


def _send_message(data_dict, body, *args):
    sqlConn = HS_mysql()
    from_user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"])
    if from_user:
        from_account = from_user[0][0]
        target_account = data_dict["target_account"]
        targe_info = search_account_by({"account":target_account}, field_list=["is_online", "fd_file"], sqlConn=sqlConn)
        target_is_online, target_fd = targe_info[0][0], targe_info[0][1]
        contact_time = changelocaltimeToSqldatetime()

        if data_dict["event"]=="send_file":
            event = "recv_file"
            type = "file"
            message = data_dict["file_name"]
        elif data_dict["event"]=="send_message":
            event = "recv_message"
            type = "message"
            message = body

        if target_is_online == b'\x01' and target_fd in global_fd_dict:
            respond_dict = {}
            respond_dict.update(data_dict)
            respond_dict.update({"event":event, "from_account":from_account,
                            "type":type, "time":contact_time})
            args[0].acquire()
            sent_result(target_fd, respond_dict, body, "text")
            args[0].release()
        if target_is_online == b'\x00' or data_dict["event"]=="send_file":
            # print("对方不在线，先存储消息到数据库")
            add_dict = {
                "account": target_account,
                "from_account": from_account,
                "message": message,
                "type": type,
                "time": contact_time
            }
            sqlConn.add("chat", add_dict)
        # 修改联系时间
        sqlConn.modify("relationship", {"time": contact_time}, "where owner_account=%s and friend_account=%s",
                       [from_account, target_account])
        sqlConn.close()
        # print("回复消息", data_dict)
    return data_dict, "success", "text"


@add_event2dict("send_message")
@check_data_dict(["cookie", "target_account"])
def send_message(fd, data_dict, body, *args):
    return _send_message(data_dict, body, *args)


@add_event2dict("send_file")
@check_data_dict(["cookie", "target_account", "event"])
def send_file(fd, data_dict, body, *args):
    print("+++++++++回复收到文件++++++++++++++", fd, data_dict, body)
    if data_dict:
        return _send_message(data_dict, body, *args)


@add_event2dict("get_message")
@check_data_dict(["cookie", "event"])
def get_message(fd, data_dict, body, *args):
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"], sqlConn=sqlConn)
    if user:
        # 查询是否有未读消息，包括文字消息和文件消息， 如果有，一条一条发送，如果没有，回复空值
        # 客户端收到消息通知后，应判断是文字还是文件，如果是文字，直接显示消息，如果是文件，应再新建套接字，发送get_file事件
        result = sqlConn.search("chat", ["id", "account", "from_account", "message", "type", "time"],
                                "where account=%s order by time desc", [user[0][0]])
        if result:
            respond_body = ""
            for i, each_result in enumerate(result):
                data_dict["from_account"] = each_result[2]
                data_dict["type"] = each_result[4]
                data_dict["time"] = each_result[5].strftime("%Y-%m-%d %H:%M:%S")
                if i < len(result)-1:
                    sent_result(fd, data_dict, each_result[3], "text")
                    if data_dict["type"]=="message":
                        sqlConn.delete("chat", "where id=%s", [each_result[0]])
                else:
                    respond_body = each_result[3]
                    if data_dict["type"] == "message":
                        sqlConn.delete("chat", "where id=%s", [each_result[0]])
            sqlConn.close()
            return data_dict, respond_body, "text"
        else:
            return {}, "", ""


@add_event2dict("get_file")
@check_data_dict(["cookie"])
def get_file(fd, data_dict, body, *args):
    print("+++++++++回复get_file++++++++++++++", fd, data_dict, body)
    sqlConn = HS_mysql()
    if "file_name" in data_dict:
        user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account", "fd_file"], sqlConn=sqlConn)
        # print("用户是", user)
        if user:
            # 查询是否有未读消息，如果有，一条一条发送，如果没有，回复空值
            result = sqlConn.search("chat", ["id", "account", "from_account", "message", "type", "time"],
                                    "where account=%s and type='file' and message=%s order by time desc", 
                                    [user[0][0], data_dict["file_name"]])
            print(f"用户{fd}的未读文件", result)
            if result:
                each_result = result[0]
                data_dict["from_account"] = each_result[2]
                data_dict["target_account"] = user[0][0]
                data_dict["type"] = each_result[4]
                data_dict["time"] = each_result[5].strftime("%Y-%m-%d %H:%M:%S")
                data_dict["file_name"] = each_result[3]
                file_path = os.path.join(HS_directory_obj.user_file_dir(data_dict["from_account"],user[0][0]),
                                     data_dict["file_name"])
                data_dict["file_path"] = file_path
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    data_dict["file_size"] = file_size
                    global_protocol_obj.send_file(global_fd_dict[fd], data_dict, timeout=30)
                sqlConn.delete("chat", "where id=%s", [each_result[0]])
            sqlConn.close()
    # 查找该用户文件，一个个发给它
    return {}, "finished", ""


@add_event2dict("get_avatar")
@check_data_dict(["cookie", "target_account", "save_path"])
def get_avatar(fd, data_dict, body, *args):
    # print("收到获取头像请求")
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account"])
    if user:
        target_user = search_account_by({"account":data_dict["target_account"]}, field_list=["account", "photo"])
        avatar_path = os.path.join(HS_directory_obj.user_avartar_dir, target_user[0][1])
        # print("该用户头像地址是", avatar_path)
        data_dict["file_name"] = target_user[0][1]
        data_dict["file_path"] = avatar_path
        global_protocol_obj.send_file(global_fd_dict[fd], data_dict, timeout=30)
        return data_dict, "success", ""
    else:
        return data_dict, "failed", ""

@add_event2dict("change_my_avatar")
@check_data_dict(["cookie", "from_account", "file_name"])
def change_my_avatar(fd, data_dict, body, *args):
    # print("收到获取头像请求")
    sqlConn = HS_mysql()
    user = search_account_by({"cookie":data_dict["cookie"]}, field_list=["account", "photo"], sqlConn=sqlConn)
    if user and user[0][0]==data_dict["from_account"]:
        data_dict["save_path"] = HS_directory_obj.user_avartar_dir
        modify_dict = {"photo": data_dict["file_name"]}
        sqlConn.modify("Contact", modify_dict, "where account=%s", params=[user[0][0]])
        try:
            os.remove(os.path.join(HS_directory_obj.user_avartar_dir, user[0][1]))
        except:
            pass
        return data_dict, "success", ""
    else:
        try:
            os.remove(os.path.join(HS_directory_obj.user_avartar_dir, data_dict["file_name"]))
        except:
            pass
        return data_dict, "failed", ""


def sent_result(fd, data_dict, body, data_type, *args):
    global global_thread_send
    global global_send_condition
    global_send_condition.acquire()
    if fd in global_thread_send:
        global_send_condition.wait()
    else:
        global_thread_send.append(fd)
        response_dict = {}
        response_dict.update(data_dict)
        response_dict["content_type"] = data_type
        if "cookie" in response_dict and "event" in response_dict and \
                response_dict["event"] != "login" and response_dict["event"] != "relogin":
            response_dict.pop("cookie")
        client_socket = global_fd_dict[fd]
        global_protocol_obj.send_data(client_socket, response_dict, str(body), 30)
        # print("回复好友信息", response_dict, body)
        global_thread_send.remove(fd)
        global_send_condition.notify()
    global_send_condition.release()


#++++++++++++++++++++++这个函数如果一直没有返回数据，那么永远无法结束select事件提醒
def client_close_event(fd, q_sent):
    # print("客户端--------------已关闭", fd)
    global_fd_dict[fd].close()
    q_sent.put({"event": "close", "fd": fd})
    clear_user_status(fd=fd)
    # if platform.system()=="Darwin":
    #     fd_dict[fd].close()
    # else:
    #     fd_dict[fd].shutdown(socket.SHUT_RDWR)  # 通知epoll客户端已经关闭，即触发select.EPOLLHUP=17
    #     # break




class Worker:
    def __init__(self):
        self.protocol_obj = MyProtocol()


    def recv_data(self, fd, data_dict, body):
        if "content_length" in data_dict and len(body.encode()) > data_dict["content_length"]:  
            # 解决粘包问题（第一次接收1024接收到两个粘包的header）
            # 实际上已经从发送端强制最小发送数据长度为1024解决
            print("粘包了", data_dict, body)
            current_size = len(body)
            have_get_header = False
            body = body.encode()
            try:
                data_dict, body = self.protocol_obj.real_recv_data({}, body, b"",
                                1024, current_size, have_get_header, global_fd_dict[fd], 30, search_account_by)
            except Exception as e:
                if b"\r\n\r\n" in body:
                    split_list = body.split(b"\r\n\r\n")
                    body = body[len(split_list[0] + b"\r\n\r\n"):]
                    header = split_list[0]
                    data_dict = json.loads(header.decode())
                else:
                    data_dict, body = {}, ""
        else:
            data_dict, body = self.protocol_obj.recv_data(global_fd_dict[fd], 30, search_account_by) 
        return data_dict, body

    def handle_event(self, fd, process_lock):
        '''
        解决多线程可能操作同一个套接字导致数据混乱问题
        解决客户端一个事件分批发送，多线程分开处理同一事件，数据不对问题
        '''
        global global_thread_recv
        try:
            # 接收
            print("start recv")
            data_dict, body = {}, b""
            while True:  # 循环处理事情
                print("继续接收，查看还有没数据")
                # data_dict, body = self.protocol_obj.recv_data(global_fd_dict[fd], 30, search_account_by) 
                data_dict, body = self.recv_data(fd, data_dict, body)
                print("接收完成", fd, data_dict, body)
                if "event" in data_dict:
                    # 处理
                    print("正在处理事件",fd, data_dict)
                    respond_data_dict, respond_body, data_type = event_fun_dict[data_dict["event"]](
                        fd, data_dict, body, process_lock)
                    # 发送
                    print("发送回复结果", fd, respond_data_dict, respond_body, data_type)
                    sent_result(fd, respond_data_dict, respond_body, data_type)
                    # print("发送完成")
                else:
                    # print("没有数据了")
                    # global_thread_recv.remove(fd)
                    break
        except Exception as e:
            print("处理事件出错",  fd, str(e))  # 如果是报没有数据或者客户端关闭的错误是正常的，因为上面就是一直循环处理，直到没有数据到来
            if "socket closed" in str(e):
                client_close_event(fd, self.q_sent)
                return
            if fd in global_thread_recv:
                global_thread_recv.remove(fd)
            self.q_sent.put({"event": "register", "fd": fd})
            traceback.print_exc()

    def get_event(self, q_recv, q_sent, fd_dict_asy, process_lock):
        # 第一次运行，修改数据库所有在线的人状态为离线
        global global_fd_dict, global_thread_recv
        global_fd_dict = fd_dict_asy  # 和其他进程同步fd_dict
        self.q_sent = q_sent
        clear_user_status()
        # print(f"我是子进程{os.getpid()}，我开始工作了")
        while True:
            # 获取套接字和  套接字词典（方便查找对应客户端）
            try:
                event_dict = q_recv.get()
                if event_dict["event"] == "read":
                    # print("++++++++我是worker，收到事件++++++++++我的fd是", global_fd_dict)
                    fd = event_dict["fd"]
                    # if fd not in global_thread_recv:  # 当没有线程占用这个fd
                    # global_thread_recv.append(fd)
                    handle_event_thread = threading.Thread(target=self.handle_event, args=(fd,  process_lock,))
                    # 记录线程信息
                    handle_event_thread.start()
                    # else:
                    #     print("忽略的事件")
            except Exception as e:
                traceback.print_exc()
                # print("处理事件出错啦", str(e))







