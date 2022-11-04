import os.path
import socket
import json
import time
import traceback
import shutil
from multiprocessing import Process
from multiprocessing import Queue

class HS_client:
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.ip = server_addr[0]
        self.port = server_addr[1]
        self.my_tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        self.my_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_tcp_socket.connect(self.server_addr)
        # print("连接成功++++++++++++++++++++")

def test():
    # print("开始连接")
    client_list=[]
    for i in range(2000):
        # print(f"正在创建第{i}个连接")
        client = HS_client(("127.0.0.1", 7999))
        client_list.append(client)
        time.sleep(0.1)  # 同时连接太快，服务器反应会跟不上
    # client_list = [HS_client(("127.0.0.1", 7999)) for i in range(2000)]
    # print("已经完成全部连接")
    while True:
        time.sleep(1)

test()
