from abc import ABC
from abc import ABCMeta, abstractmethod
import socket


class HS_socket:
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.ip = server_addr[0]
        self.port = server_addr[1]
        self.my_tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        self.my_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_tcp_socket.settimeout(60)
        self.my_tcp_socket.connect(self.server_addr)
        self.my_tcp_socket.settimeout(None)
        self.my_tcp_socket.getpeername()
        # print("连接成功++++++++++++++++++++")


class Client(ABC):
    def __init__(self):
        print("我是抽象客户端")

    @abstractmethod
    def handle_GUI_event(self, header_dict, body): pass

    @abstractmethod
    def start_work(self): pass

    @abstractmethod
    def stop_work(self): pass


def get_current_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        if "Network is unreachable" in str(e):
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return ""
        else:
            return ""
    finally:
        s.close()
    return ip