file_share.py
import os
import time
from multiprocessing import Process
import traceback
import socket
import threading
import json
import sys
import re
import shutil


class Protocol:
    def __init__(self):
        pass

    def send_data(self, socket_fileobj, header_dict={}, body="", timeout=None, *args, **kwargs):
        '''
            socket_fileobj 套接字对象
            header_dict 是发送数据的头部，指定发送的信息是文字还是文件类型，数据的有效长度；默认类型为文字
            头部信息和有效数据用"\r\n\r\n"隔开，接收数据时，检测第一个"\r\n\r\n"分割头部和有效数据
            body 是发送的实际内容，类型为字符串，而不是二进制
        '''
        if timeout is not None:
            socket_fileobj.settimeout(timeout)
        body_byte = body.encode()
        if "content_type" not in header_dict:
            header_dict["content_type"] = "text"
        if "content_length" not in header_dict: # 如果发送文件头部，需要指定文件大小
            header_dict["content_length"] = len(body_byte)
        header_byte = json.dumps(header_dict).encode() + f"\r\n\r\n".encode()
        if len(header_byte)<1024:
            header_byte += (" ".encode())*(1024-len(header_byte))  # 凑够1024字节发，防止对方一次接收1024粘包（比如连续发送两个小的header，就会把第二个header也接收下来了）
        socket_fileobj.sendall(header_byte  + body_byte)

    def recv_header(self, socket_fileobj, timeout=None):
        if timeout is not None:
            socket_fileobj.settimeout(timeout)
        header, body= b"", b""
        while True:
            data = socket_fileobj.recv(1024) # 这里可能会收到两个连续的header
            if data == b"":
                raise Exception("socket closed")
            header += data
            if b"\r\n\r\n" in header:
                split_list = header.split(b"\r\n\r\n")
                index = len(split_list[0] + b"\r\n\r\n")
                if index <= 1024: # 头部最小是1024
                    index = 1025
                body = header[index:]
                header_dict = json.loads(split_list[0].decode())
                return header_dict, body

    def recv_body(self, socket_fileobj, header_dict, body):
        '''
        body 是接收头部时多接收到的body
        '''
        current_size = len(body)
        while True:
            if header_dict["content_length"] == current_size or header_dict["content_length"] == 0:
                return body.decode()
            elif header_dict["content_length"] - current_size < 1024:
                recv_lenght = header_dict["content_length"] - current_size 
            else:
                recv_lenght = 1024
            data = socket_fileobj.recv(recv_lenght)
            body += data
            current_size += len(data)

    def recv_data(self, socket_fileobj, timeout=None, *args, **kwargs):
        '''
        一次性接收header和body
        '''
        if timeout is not None:
            socket_fileobj.settimeout(timeout)  # 防止服务器没有回应，程序卡在这里
        header_dict, body = self.recv_header(socket_fileobj)
        body = self.recv_body(socket_fileobj, header_dict, body)
        return header_dict, body


class FileProtocol(Protocol):
    def __init__(self):
        '''
        每次只发送/接收一个文件
        '''
        super().__init__()

    def send_file(self, file_path, socket_fileobj, timeout=None, *args, **kwargs):
        '''
        kwargs可以带basedir，表示发送文件夹时的文件夹路径，接收时，在file_path的基础上移除这个basedir，剩下的路径如果是多层级目录
        则创建一样的多层级目录保存
        '''
        if timeout is not None:
            socket_fileobj.settimeout(timeout)  # 防止服务器没有回应，程序卡在这里
        file_size = os.path.getsize(file_path)
        header_dict = {}
        if kwargs:
            header_dict.update(kwargs)
        header_dict["content_length"] = file_size
        header_dict["file_path"] = file_path
        header_dict["content_type"] = "file"
        self.send_data(socket_fileobj, header_dict)
        current_size = 0
        print(f"发送文件...{file_path}...", header_dict)
        with open(file_path, "rb") as f:
            while True:
                if file_size - current_size < 1024 * 1024: # 就算size为0也能发送出去
                    socket_fileobj.sendall(f.read(file_size - current_size))
                    break
                else:
                    socket_fileobj.sendall(f.read(1024 * 1024))
                    current_size += 1024 * 1024
        print("等待对方接收...", end="")
        header_dict, body = self.recv_data(socket_fileobj, timeout=100) # 等待对方接收
        print("finished!")

    def send_file_folder(self, file_folder_path, socket_fileobj, timeout=None, *args, **kwargs):
        if os.path.isdir(file_folder_path):
            # fix 服务器每发送一个文件，回复客户端一次事件，而客户端只接收一次回复的问题
            # todo 如何判断os.walk 次数到了最后一次？
            event = ''
            if "event" in kwargs:
                event = kwargs["event"]
                kwargs.pop("event")
            path_l = []
            basedir = os.path.dirname(file_folder_path)
            for root, dirs, files in os.walk(file_folder_path):
                for name in files:
                    path_l.append(os.path.join(root, name))
            for i, path in enumerate(path_l):
                if i==len(path_l)-1 and event:
                    kwargs["event"] = event
                self.send_file(path, socket_fileobj, timeout, basedir=basedir,  *args, **kwargs)
        else:
            self.send_file(file_folder_path, socket_fileobj, timeout, *args, **kwargs)
        print("文件已全部发送")

    def get_save_path(self, savedir, header_dict):
        '''
        如果savedir不存在，则保存到系统下载目录
        如果basedir存在，则创建多层级目录
        '''
        if not os.path.exists(savedir):
            savedir = os.path.join(os.path.expanduser("~"),"Downloads")
        file_path = header_dict["file_path"]
        if '\\' in file_path: # windows分隔符在linux上面不识别
            file_path = file_path.replace("\\", os.sep)
        # 保存文件名
        filename = os.path.basename(file_path)
        # 检查是否创建子目录
        if "basedir" in header_dict:
            basedir = header_dict["basedir"] if '\\' not in header_dict["basedir"] else header_dict["basedir"].replace("\\", os.sep)
            child_dir = re.search(f'{basedir}{os.sep}(.*?){os.sep}{filename}$', file_path)
            if child_dir is not None:
                for i in child_dir.group(1).split(os.sep):
                    if not os.path.exists(os.path.join(savedir, i)):
                        os.mkdir(os.path.join(savedir, i))
                    savedir = os.path.join(savedir, i)
        save_path = os.path.join(savedir, filename)
        return save_path

    def recv_file(self, savedir, socket_fileobj, timeout=None, *args, **kwargs):
        '''
            当指定header_dict, body时，则此函数不接收header_dict, body
        '''
        if timeout is not None:
            socket_fileobj.settimeout(timeout)  # 防止服务器没有回应，程序卡在这里
        if kwargs:
            header_dict, body = kwargs["header_dict"], kwargs["body"]
        else:
            header_dict, body = self.recv_header(socket_fileobj)
        # windows的分隔符\\无法用os.path.basename()
        save_path = self.get_save_path(savedir, header_dict)
        print(f"接收文件...{save_path}...", end="")
        header_dict["save_path"] = save_path
        with open(save_path, "wb") as f:
            f.write(body)
            left_size = int(header_dict["content_length"]) - len(body)
            current_size = 0
            while True:
                if left_size - current_size < 1024 * 1024:
                    recv_data = socket_fileobj.recv(left_size - current_size)
                    f.write(recv_data)
                    current_size += len(recv_data)
                    if current_size == left_size:
                        break
                else:
                    recv_data = socket_fileobj.recv(1024 * 1024)
                    f.write(recv_data)
                    current_size += len(recv_data)  # 实际接收到的数据是缓冲区存在的最大数据，而不是1024*1024
                if recv_data == b"":
                    raise Exception("socket closed")
            self.send_data(socket_fileobj, body="finised recv file!")
            print(f"finished!")
            return header_dict


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                               发送和接收文件的例子
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Send_file_process(Process):
    def __init__(self, file_path, target_addr):
        super().__init__()
        self.file_path = file_path
        client = Client(target_addr)
        self.socket_fileobj = client.my_tcp_socket
        self.tcp_protocol_obj = FileProtocol()

    def run(self):
        try:
            self.tcp_protocol_obj.send_file_folder(self.file_path, self.socket_fileobj, timeout=30)
        except Exception as e:
            print("运行发送文件函数出错", str(e))
            traceback.print_exc()

# 发送
def send_file(file_path, target_addr):
    send_file_process_obj = Send_file_process(file_path, target_addr)
    send_file_process_obj.start()


class Client:
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.my_tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        self.my_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_tcp_socket.settimeout(60)
        self.my_tcp_socket.connect(self.server_addr)
        self.my_tcp_socket.settimeout(None)
        self.my_tcp_socket.getpeername()
        print("连接成功++++++++++++++++++++")

# 接收
class Server:
    def __init__(self, ip, port, savedir=''):
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许地址复用， 防止关闭程序后此连接还在，重新打开程序报地址已被连接的错误
        self.ip = ip
        try:
            self.server_socket.bind((self.ip, port))
            self.server_socket.listen(128)
        except Exception as e:
            print("绑定地址失败", str(e))
        self.tcp_protocol_obj = FileProtocol()
        self.savedir = savedir if savedir else os.path.join(os.path.expanduser("~"),"Downloads")

    def accept(self):
        while True:
            try:
                print("内部服务器等待接收连接")
                client_socket, client_address = self.server_socket.accept()
                print("内部服务器收到连接")
                handle_client_t = threading.Thread(target=self.handle_client, args=(client_socket, client_address, ))
                handle_client_t.start()
            except:
                break
            time.sleep(0.1)

    def handle_client(self, client_socket, client_address):
        try:
            while True:
                header_dict, body = self.tcp_protocol_obj.recv_header(client_socket)
                if header_dict["content_type"]=="file":
                    self.tcp_protocol_obj.recv_file(self.savedir, client_socket, 120, header_dict=header_dict, body=body)
        except Exception as e:
            if "socket closed" in str(e):
                print("接收文件完成")
            else:
                traceback.print_exc()
                print("接收数据出错", str(e))


def print_help():
    print(f"send file: python3 fileshare.py sendfile target_ip:port filepath/dir")
    print(f"receive file: python3 fileshare.py recvfile my_ip:port savedir")
    print("plese run the receive file before send file!")


if __name__ == "__main__":
    parameter = sys.argv
    if len(parameter)==1:
        print_help()
    elif parameter[1]=="sendfile":
        addr = (parameter[2].split(":")[0], int(parameter[2].split(":")[1]))
        file_path = parameter[3]
        send_file(file_path, addr)
    elif parameter[1]=="recvfile":
        addr = tuple(parameter[2].split(":"))
        savedir = parameter[3]
        server = Server(addr[0], int(addr[1]), savedir)
        server.accept()
    else:
        print_help()
        
    




