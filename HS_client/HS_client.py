import os
import sys
import socket
import threading

from HS_offline_client import HS_offline_client
from HS_online_client import HS_online_client




def get_GUI_event(q_recv, HS_online_client_obj, HS_offline_client_obj):
    while True:
        [header_dict, body] = q_recv.get()
        print("收到GUI事件", header_dict, body)
        if "event" in header_dict:  # 处理事件
            if HS_online_client_obj.am_i_running:
                print("在线处理")
                if HS_offline_client_obj.am_i_running:
                    HS_offline_client_obj.stop_work()
                HS_online_client_obj.handle_GUI_event(header_dict, body)
            else:
                if not HS_offline_client_obj.am_i_running:
                    HS_offline_client_obj.start_work()
                HS_offline_client_obj.handle_GUI_event(header_dict, body)


def start_work(q_sent, q_recv):
    HS_online_client_obj = HS_online_client(q_sent, q_recv)
    HS_offline_client_obj = HS_offline_client(q_sent, q_recv)
    # 接收GUI事件
    start_get_GUI_event = threading.Thread(target = get_GUI_event, args=(q_recv, HS_online_client_obj, HS_offline_client_obj, ))
    start_get_GUI_event.daemon = True
    start_get_GUI_event.start()
    # 接收服务器信息
    HS_online_client_obj.start_work()



