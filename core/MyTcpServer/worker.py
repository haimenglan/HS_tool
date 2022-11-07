Worker.py
import threading
import traceback
import os

from fileshare import Protocol, FileProtocol
import event

global_fd_dict = {}
global_file_save_dir = os.path.dirname(__file__)

class Worker:
    def __init__(self):
        self.protocol_obj = Protocol()
        self.file_protocol_obj = FileProtocol()
        self.savedir = global_file_save_dir if global_file_save_dir else os.path.expanduser("~")

    def handle_event(self, fd, process_lock):
        '''
        注意如果是同一个客户端发送来多个事件，每个到来的事件都开启一个线程处理，会有问题：
        多线程处理同一个套接字可能会有冲突: 如果这里的数据还没接收完成，另一个线程可能会把数据接收掉
        这里的解决方案是，服务器收到事件，交给worker后立马移除此套接字的监听，而worker在这里用while true不断接收事件，直到再无事件到来，通知服务器恢复监听
        同样的，这里多线程给同一个客户端发送消息也可能会起冲突
        '''
        try:
            while True:
                # 接收
                header_dict, body = self.protocol_obj.recv_header(global_fd_dict[fd], timeout=30)
                # print("收到头部", header_dict, "收到body", body)
                if header_dict["content_type"] == "file":
                    header_dict = self.file_protocol_obj.recv_file(self.savedir, global_fd_dict[fd], 120, header_dict=header_dict, body=body)
                else:
                    body = self.protocol_obj.recv_body(global_fd_dict[fd], header_dict, body)
                # 处理
                if "event" in header_dict:
                    respond_dict, respond_body = event.event_fun_dict[header_dict["event"]](global_fd_dict[fd], header_dict, body, process_lock)
                    # 回复客户端
                    # if respond_body or respond_dict:
                    self.protocol_obj.send_data(global_fd_dict[fd], respond_dict, respond_body, timeout=30)
        except Exception as e:
            traceback.print_exc()
            # 客户端关闭， 通知服务器移除此套接字
            if "socket closed" in str(e):
                global_fd_dict[fd].close()
                self.q_sent.put({"event": "close", "fd": fd})
                return
            # 客户端无消息，通知服务器重新监听此套接字（因为服务器一收到事件立马移除监听）
            print("重新注册")
            self.q_sent.put({"event": "register", "fd": fd})

    def get_event(self, q_recv, q_sent, fd_dict_asy, process_lock):
        '''
        通过queue 监听服务器事件，并交给多线程处理
        '''
        global global_fd_dict
        global_fd_dict = fd_dict_asy  # 和其他进程同步fd_dict
        self.q_sent = q_sent
        while True:
            # 获取套接字和套接字词典（方便查找对应客户端）
            try:
                event_dict = q_recv.get()
                if event_dict["event"] == "read":
                    # print("++++++++我是worker，收到事件++++++++++我的fd是", global_fd_dict)
                    fd = event_dict["fd"]
                    handle_event_thread = threading.Thread(target=self.handle_event, args=(fd,  process_lock,))
                    handle_event_thread.start()
            except Exception as e:
                traceback.print_exc()








