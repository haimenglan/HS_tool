from multiprocessing import freeze_support
freeze_support()
from multiprocessing import Process
from multiprocessing import Queue
import time
import os
import sys
sys.path.append(os.path.dirname(__file__))
search_path = ['C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1', 'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_GUI',
'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_client','C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_tool_tool',
'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_universal',
]
for each_path in search_path:
    sys.path.append(each_path)

from HS_client import HS_client
from HS_GUI.HS_login_GUI import  Login_app


def main():
    q_sent, q_recv = Queue(10), Queue(10)
    start_client_p = Process(target=HS_client.start_work, args=(q_recv, q_sent, ))
    # start_client_p.daemon = True
    start_client_p.start()
    Login_app(q_sent, q_recv)
    start_client_p.terminate()


if __name__ == "__main__":
    main()