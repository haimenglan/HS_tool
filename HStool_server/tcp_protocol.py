from abc import ABC
from abc import ABCMeta, abstractmethod
import json
import os
import shutil
import datetime

from HS_directory import HS_directory
HS_directory_obj = HS_directory()

def zip_folder(folder_path):
    """
    压缩文件(夹)为zip格式：
    指令shutil.make_archive, 可选参数如下：
        1.base_name： 生成的压缩包的名字或者路径，不带.zip后缀的。
            1) 给的是路径，例如 D:\a\b 将在D盘a文件夹下生成一个b.zip的压缩包
            2）如果带”.zip“，比如D:\a\b.zip 将在D盘a文件夹生成一个b.zip.zip的压缩包
            3）给的只有压缩包名字则在当前工作目录（python工作目录下）生成”名字.zip“
        2.format： 压缩包种类，“zip”, “tar”, “bztar”，“gztar”
        3.root_dir: 如果不指定base_dir, 则是要压缩的文件夹路径，如果指定了basedir？
        4.base_dir： 如果root_dir 和 base_dir都是folder_path, 则压缩后的文件会包含系统的全路径
    """
    base_name = folder_path  # 生成的压缩文件位置为 要压缩的文件夹所在路径
    zip_path = shutil.make_archive(base_name, "zip", root_dir=os.path.dirname(folder_path),
                                   base_dir=os.path.basename(folder_path))
    return zip_path

class TcpProtocol(ABC):
    # __metaclass__ = ABCMeta
    def __init__(self):
        print("我是抽象协议")

    @abstractmethod
    def send_data(self, fileobj, header_dict, body, timeout=None, *args, **kwargs):
        '''
        发送header_dict(参数) 和body(内容)
        '''
        print("发送抽象协议")

    @abstractmethod
    def recv_data(self, fileobj, timeout=None, *args, **kwargs):
        '''
        返回header_dict(参数) 和body(内容)
        '''
        pass

    @abstractmethod
    def parse_data(self, header_dict, body):
        '''
        解析body内容
        '''
        pass

    @abstractmethod
    def send_file(self, fileobj, header_dict, *args, **kwargs):
        '''
        参数必须包含：file_path = header_dict["file_path"]
        '''
        pass

    @abstractmethod
    def recv_file(self, fileobj, header_dict, body, timeout=None, *args, **kwargs):
        '''
        接收完成把文件保存路径放在header_dict["save_path"]
        '''
        pass


class MyProtocol(TcpProtocol):
    def __init__(self, file_save_path='', buffer_path=''):
        '''

        '''
        super().__init__()
        if file_save_path:
            self.file_save_path = file_save_path
        if buffer_path:
            self.buffer_path = buffer_path
        print("我是自己的协议")

    def send_data(self, fileobj, header_dict, body, timeout=None, *args, **kwargs):
        if timeout is not None:
            fileobj.settimeout(timeout)
        body_byte = body.encode()
        if header_dict:
            if "content_type" not in header_dict:
                header_dict["content_type"] = "text"
            header_dict["content_length"] = len(body_byte)
        total_data = json.dumps(header_dict).encode() + f"\r\n\r\n".encode() + body_byte
        if len(total_data)<1024:
            total_data += (" ".encode())*(1024-len(total_data))  # 凑够1024字节发，防止对方一次接收1024粘包
        fileobj.sendall(total_data)

    def real_recv_data(self, header_dict, header, body,
                       recv_lenght, current_size, have_get_header,  fileobj, timeout=None, *args, **kwargs):
        data = fileobj.recv(recv_lenght)
        if data == b"":
            raise Exception("socket closed")
        # todo 限定接收数据大小
        current_size += len(data)
        if not have_get_header:
            header += data
        else:
            body += data
        if b"\r\n\r\n" in header:
            have_get_header = True
            split_list = header.split(b"\r\n\r\n")
            body = header[len(split_list[0] + b"\r\n\r\n"):]
            header = split_list[0]
            header_dict = json.loads(header.decode())
            current_size = len(body)
            print("收到头部", header_dict)
            if header_dict["content_type"] == "file":
                header_dict = self.recv_file(fileobj, header_dict, body, timeout, *args, **kwargs)
                return self.parse_data(header_dict, b"")
        if "content_length" in header_dict:  # 如果指定长度接收
            if header_dict["content_length"] - current_size < 1024:
                recv_lenght = header_dict["content_length"] - current_size
                print("待接收长度为", recv_lenght)
            if header_dict["content_length"] == current_size:
                return self.parse_data(header_dict, body)
            if header_dict["content_length"] == 0 or recv_lenght <= 0:
                return self.parse_data(header_dict, body)
            header_dict, body = self.real_recv_data(header_dict, header, body,
                                recv_lenght, current_size, have_get_header, fileobj, timeout, *args, **kwargs)
            return header_dict, body
        else:
            try:
                header_dict, body = self.real_recv_data(header_dict, header, body,
                       recv_lenght, current_size, have_get_header,  fileobj, timeout, *args, **kwargs)
            except Exception as e:
                if "socket closed" not in str(e):
                    return self.parse_data(header_dict, body)
                else:
                    raise Exception("socket closed")

    def recv_data(self, fileobj, timeout=None, *args, **kwargs):
        header, body = b"", b""
        header_dict = {}
        recv_lenght = 1024
        current_size = 0
        have_get_header = False
        if timeout is not None:
            fileobj.settimeout(timeout)  # 防止服务器没有回应，程序卡在这里
        return self.real_recv_data(header_dict, header, body,
                       recv_lenght, current_size, have_get_header,  fileobj, timeout, *args, **kwargs)
        # while True:
        #     data = fileobj.recv(recv_lenght)
        #     if data == b"":
        #         raise Exception("socket closed")
        #     # todo 限定接收数据大小
        #     current_size += len(data)
        #     if not have_get_header:
        #         header += data
        #     else:
        #         body += data
        #     if b"\r\n\r\n" in header:
        #         have_get_header = True
        #         split_list = header.split(b"\r\n\r\n")
        #         body = header[len(split_list[0] + b"\r\n\r\n"):]
        #         header = split_list[0]
        #         header_dict = json.loads(header.decode())
        #         current_size = len(body)
        #         print("收到头部", header_dict)
        #         if header_dict["content_type"]=="file":
        #             header_dict = self.recv_file(fileobj, header_dict, body, timeout, *args, **kwargs)
        #             return self.parse_data(header_dict, b"")
        #     if "content_length" in header_dict:  # 如果指定长度接收
        #         if header_dict["content_length"] - current_size < 1024:
        #             recv_lenght = header_dict["content_length"] - current_size
        #             print("待接收长度为", recv_lenght)
        #         if header_dict["content_length"] == current_size:
        #             return self.parse_data(header_dict, body)
        #         if header_dict["content_length"]==0 or recv_lenght<=0:
        #             return self.parse_data(header_dict, body)
        #     else:
        #         # todo 这里应该怎么做？
        #         return self.parse_data(header_dict, body)

    def parse_data(self, header_dict, body):
        print("收到的body是", header_dict, body)
        if "content_length" in header_dict and len(body)>header_dict["content_length"]:
            body = body[:header_dict["content_length"]]
        body = body.decode()
        if header_dict["content_type"]=="eval" and body:
            body=eval(body)
        return header_dict, body

    def send_file(self, fileobj, header_dict, timeout=None,  *args, **kwargs):
        if timeout is not None:
            fileobj.settimeout(timeout)  # 防止服务器没有回应，程序卡在这里
        file_path = header_dict["file_path"]
        # print("开始发文件", file_path)
        if os.path.isdir(header_dict["file_path"]):
            # 先压缩成一个文件再发送
            file_path = zip_folder(header_dict["file_path"])
            # print("压缩文件得到的路径是", file_path)
        file_size = os.path.getsize(file_path)
        header_dict["content_length"] = file_size
        header_dict["file_name"] = os.path.basename(file_path)
        # if "content_type" not in header_dict:
        header_dict["content_type"] = "file"
        print("我是发送文件函数， 我所在的进程是", os.getpid(), "我要发送的数据是", header_dict, )
        current_size = 0
        with open(file_path, "rb") as f:
            fileobj.sendall(json.dumps(header_dict).encode() + f"\r\n\r\n".encode())  # 发送头
            # fileobj.sendfile(f)  仅在windows可用
            # print("发送文件", header_dict)
            while True:
                # print("发送文件中")
                if file_size - current_size < 1024 * 1024:
                    fileobj.sendall(f.read(file_size - current_size))
                    # print("文件发送完成")
                    break
                else:
                    fileobj.sendall(f.read(1024 * 1024))
                    current_size += 1024 * 1024
            print("发送文件完成", header_dict["file_name"])

    def get_save_path(self, header_dict, from_account:str=""):
        if "save_path" in header_dict and os.path.isdir(header_dict["saev_path"]):
            save_path = os.path.join(header_dict["saev_path"], header_dict["file_name"])
        elif "target_account" in header_dict:
            save_path = os.path.join(HS_directory_obj.user_file_dir(from_account, header_dict["target_account"]),
                                 header_dict["file_name"])
        elif header_dict["event"] =="change_my_avatar":
            save_path = os.path.join(HS_directory_obj.user_avartar_dir, header_dict["file_name"])
        else:
            save_path = os.path.join(HS_directory_obj.file, header_dict["file_name"])
        return save_path

    def recv_file(self, fileobj, header_dict, body, timeout=None, *args, **kwargs):
        user = args[0]({"cookie":header_dict["cookie"]}, field_list=["account"])  # args[0]是查询账号的函数
        if user:
            from_account = user[0][0]
            save_path = self.get_save_path(header_dict, from_account)
            header_dict["save_path"] = save_path
            # print("保存路径是", save_path)
            with open(save_path, "wb") as f:
                f.write(body)
                # print("body大小", len(body))
                left_size = int(header_dict["content_length"]) - len(body)
                # print("剩余未接收大小", left_size, "总大小", len(body) + left_size)
                current_size = 0
                while True:
                    if left_size - current_size < 1024 * 1024:
                        # print("接收", left_size - current_size)
                        recv_data = fileobj.recv(left_size - current_size)
                        f.write(recv_data)
                        current_size += len(recv_data)
                        # print("已收到", current_size)
                        if current_size == left_size:
                            # print("文件接收完成", current_size)
                            break
                    else:
                        # print("接收1024*1024")
                        recv_data = fileobj.recv(1024 * 1024)
                        f.write(recv_data)
                        current_size += len(recv_data)  # 实际接收到的数据是缓冲区存在的最大数据，而不是1024*1024
                    if recv_data == b"":
                        raise Exception("socket closed")
                print("文件接收完成++++++++++++++++++++++")
                return header_dict


class HttpProtocol(TcpProtocol):
    def __init__(self):
        super().__init__()
        print("我是http协议")

    def send_data(self, fileobj, header_dict, body, *args, **kwargs):
        print("发送http数据")

    def recv_data(self, fileobj, timeout=None, *args, **kwargs):
        pass

    def parse_data(self, header_dict, body):
        pass

    def send_file(self, fileobj, header_dict, *args, **kwargs):
        pass

    def recv_file(self, fileobj, header_dict, body, timeout=None, *args, **kwargs):
        pass