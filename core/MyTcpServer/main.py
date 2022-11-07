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
        self.fd_dict = multiprocessing.Manager().dict() # 多进程共享变量
        self.my_fd_dict = {}
        # 把监听连接套接字也交给系统监听
        self.add_socket(server_socket)


    def listen(self, server_socket):
        client_socket, client_address = server_socket.accept()
        self.add_socket(client_socket)

    def add_socket(self, fileobj):
        # 注册套接字，一旦注册，系统会帮忙监听套接字事件
        self.selector.register(fileobj, selectors.EVENT_READ)
        # 多进程共享套接字
        self.fd_dict[fileobj.fileno()] = fileobj
        # 保存本进程已注册的套接字
        self.my_fd_dict[fileobj.fileno()] = fileobj

    def unregister_only(self, fd):
        # 从系统监听移除本进程的套接字（系统只监听本进程的套接字，而不管其它多进程的）
        self.selector.unregister(self.my_fd_dict[fd])

    def remove(self, fd):
        """
        只能取消注册此进程下面的套接字，子进程的套接字是复制的，取消不了。
        self.fd_dict字典每个进程保存的套接字ip地址是一样的，但fd文件不一样，子进程相当于复制了一份fd文件,
        因此如果子进程告诉本进程，我要取消注册fd=22， 本进程无法根据fd=22取消注册对应的本进程套接字
        简而言之，本进程的self.fd_dict[22] != 子进程的self.fd_dict[22]
        因此需要通过self.selector._fd_to_key 找到本进程的套接字来取消注册
        """
        if fd in self.fd_dict:
            if fd in self.selector._fd_to_key:
                fileobj = self.selector._fd_to_key[fd].fileobj  # 查看本进程下注册了哪些fd
                self.selector.unregister(fileobj)
            self.fd_dict[fd].close()
            self.my_fd_dict[fd].close()
            self.fd_dict.pop(fd)
            self.my_fd_dict.pop(fd)


    def handle(self, fileobj, fd, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        '''
        阻塞等待事件到来，如果是连接请求事件，则listen创新新的套接字服务
        如果是客户端事件请求，则将此套接字转给子进程处理，本进程取消注册此套接字，不再监听来自它的事件（因为此时不管该套接字发来什么数据，子进程都会接收）
        '''
        while True:
            event_lists = self.selector.select()  # 阻塞
            for key, mask in event_lists:
                this_socket = key.fileobj
                this_fd = key.fd
                if this_fd == self.server_fd:
                    self.listen(this_socket)
                else:
                    self.handle(this_socket, this_fd, *args, **kwargs)
                    # 移除监听，防止接收数据时不断收到通知，等事件处理完成再恢复监听
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
        # 讲此fd从原来的worker中移除
        for i, each_worker in enumerate(self.worker_fd_list):
            if fd in each_worker:
                self.worker_fd_list[i].remove(fd)
                break

    def handle(self, fileobj, fd, *args, **kwargs):
        super().handle(fileobj, fd)
        is_old_fd = False  # 之前分配过的fd只转交给给之前分配给的worker处理，防止同一时间不同worker使用同一个套接字同时传输数据造成数据混乱
        for i, each_worker in enumerate(self.worker_fd_list):
            if fd in each_worker:
                self.worker_q_sent[i].put({"event":"read", "fd":fd})
                is_old_fd = True
                break
        if not is_old_fd: # 转交给新的worker
            self.worker_fd_list[self.current_worker].append(fd)
            self.worker_q_sent[self.current_worker].put({"event":"read", "fd":fd})
            self.current_worker += 1
        if self.current_worker >= len(self.worker_q_sent):
            self.current_worker = 0

    def listen_worker(self):
        # 监听子进程发来的事件
        while True:
            event_dict = self.worker_q_recv.get()
            if event_dict["event"] == "close":
                self.remove(event_dict["fd"])
            if event_dict["event"] == 'register':
                fd = event_dict["fd"]
                self.selector.register(self.my_fd_dict[fd], selectors.EVENT_READ)

    def run(self):
        '''
        运行服务器
        '''
        process_lock = Lock()
        w = Worker()
        for i, each_q in enumerate(self.worker_q_sent):
            worker_p = Process(target=w.get_event, args=(each_q, self.worker_q_recv, self.fd_dict, process_lock,))
            worker_p.start()
        time.sleep(2)
        listen_worker_t = threading.Thread(target=self.listen_worker)
        listen_worker_t.daemon = True
        listen_worker_t.start()
        super().run()


def main(ip, port):
    print("启动服务器", ip, port)
    m = Manager(ip, port)
    m.run()



if __name__ == "__main__":
    main("127.0.0.1", 6677)