import socket
import select
import selectors
import platform
from time import sleep
import time
import multiprocessing
from multiprocessing import Process, Lock
from multiprocessing import Queue
import threading
import traceback
import worker
from worker import Worker


class Loop:
    def __init__(self, ip, port):
        server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # 创建tcp套接字 服务器
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许地址复用， 防止关闭程序后此连接还在，重新打开程序报地址已被连接的错误
        server_socket.bind((ip, port))
        server_socket.listen(2048)
        self.selector = selectors.DefaultSelector()
        self.server_fd = server_socket.fileno()
        self.fd_dict = multiprocessing.Manager().dict()
        self.my_fd_dict = {}
        self.add_socket(server_socket)


    def listen(self, server_socket):
        client_socket, client_address = server_socket.accept()
        self.add_socket(client_socket)

    def add_socket(self, fileobj):
        self.selector.register(fileobj, selectors.EVENT_READ)
        # print("注册", fileobj)
        self.fd_dict[fileobj.fileno()] = fileobj
        self.my_fd_dict[fileobj.fileno()] = fileobj
        # print("当前连接数目", len(self.fd_dict))

    def unregister_only(self, fd):
        self.selector.unregister(self.my_fd_dict[fd])

    def remove(self, fd):
        """
        只能取消注册此进程下面的套接字，子进程的套接字是复制的，取消不了。fd_dict字典每个进程保存的套接字地址是一样的，
        但套接字的fd不一样，子进程相当于复制了一份fd
        """
        # print("当前注册的有", self.selector._fd_to_key)
        if fd in self.fd_dict:
            # print("取消注册", fd, self.fd_dict[fd])
            # print("要取消注册的是", self.selector._fd_to_key)
            if fd in self.selector._fd_to_key:
                fileobj = self.selector._fd_to_key[fd].fileobj  # 查看本进程下注册了哪些fd
                self.selector.unregister(fileobj)
            # print("注册成功")
            self.fd_dict[fd].close()
            self.my_fd_dict[fd].close()
            self.fd_dict.pop(fd)
            self.my_fd_dict.pop(fd)


    def handle(self, fileobj, fd, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        while True:
            # print("等待")
            event_lists = self.selector.select()  # 阻塞
            print("事件到来", event_lists, self.fd_dict)
            for key, mask in event_lists:
                this_socket = key.fileobj
                this_fd = key.fd
                # print("+" * 50, this_socket, this_fd)
                if this_fd == self.server_fd:
                    # print("有新的连接")
                    self.listen(this_socket)
                else:
                    # print("有新事件, 我是manager，我的fd是", self.my_fd_dict,  "公共fd是", self.fd_dict)
                    self.handle(this_socket, this_fd, *args, **kwargs)
                    self.unregister_only(this_fd)


class Manager(Loop):
    def __init__(self, ip, port):
        self.worker_q_sent = [Queue(10), Queue(10), Queue(10), Queue(10)]
        self.worker_q_recv = Queue(10)
        self.worker_fd_list = [[], [], [], []]  # 记录哪个进程管理哪些fd
        self.current_worker = 0
        super().__init__(ip, port)

    def remove(self, fd):
        super().remove(fd)
        for i, each_worker in enumerate(self.worker_fd_list):
            if fd in each_worker:
                self.worker_fd_list[i].remove(fd)
                break

    def handle(self, fileobj, fd, *args, **kwargs):
        super().handle(fileobj, fd)
        # print("开始处理事件")
        is_old_fd = False  # 之前分配过的fd只能给之前分配给的worker，防止不同worker使用同一个套接字同时传输数据造成数据混乱
        for i, each_worker in enumerate(self.worker_fd_list):
            if fd in each_worker:
                # print(f"事件转交给worker {i}")
                self.worker_q_sent[i].put({"event":"read", "fd":fd})
                is_old_fd = True
                break
        if not is_old_fd:
            # print(f"事件转交给worker {self.current_worker}")
            self.worker_fd_list[self.current_worker].append(fd)
            self.worker_q_sent[self.current_worker].put({"event":"read", "fd":fd})
            self.current_worker += 1
        if self.current_worker >= len(self.worker_q_sent):
            self.current_worker = 0

    def listen_worker(self):
        while True:
            event_dict = self.worker_q_recv.get()
            if event_dict["event"] == "close":
                # print("关闭事件", event_dict["fd"])
                self.remove(event_dict["fd"])
            if event_dict["event"] == 'register':
                print("重新注册")
                fd = event_dict["fd"]
                self.selector.register(self.my_fd_dict[fd], selectors.EVENT_READ)
                # print("重新注册后我的fd是", self.my_fd_dict)


    def run(self):
        # print("开启多进程处理事件")
        process_lock = Lock()
        worker.clear_user_status()
        w = Worker()
        for i, each_q in enumerate(self.worker_q_sent):
            # print("启动进程", i)
            worker_p = Process(target=w.get_event, args=(each_q, self.worker_q_recv, self.fd_dict, process_lock,))
            worker_p.start()
        time.sleep(2)
        listen_worker_t = threading.Thread(target=self.listen_worker)
        listen_worker_t.daemon = True
        listen_worker_t.start()
        super().run()