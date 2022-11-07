Client.py
import socket
import fileshare
from fileshare import Protocol, FileProtocol

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


def main():
    myClient = Client(("127.0.0.1", 6677))
    protocol_obj = Protocol()
    file_protocol_obj = FileProtocol()
    protocol_obj.send_data(myClient.my_tcp_socket, header_dict={"event":"example_event"}, body="hallo i am haimeng", timeout=30)
    respond_dict, respond_body = protocol_obj.recv_data(myClient.my_tcp_socket)
    print("收到回复",respond_dict, respond_body)
    # 发送文件夹，因为包含多个文件，相当于连续发送多个事件，收不到服务器回复
    file_protocol_obj.send_file_folder("/Users/js-15400155/Desktop/工作", myClient.my_tcp_socket,
                                timeout=30, event="example_event2")
    respond_dict, respond_body = protocol_obj.recv_data(myClient.my_tcp_socket)
    print("收到回复2", respond_dict, respond_body)

if __name__ == "__main__":
    main()