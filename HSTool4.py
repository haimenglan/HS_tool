import multiprocessing
multiprocessing.freeze_support()
#! /usr/bin/env python3.7
# ! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7

'''
蓝海梦的小程序
atlas-metadata -s "Station-Type" -d productID -p "User Defined Signing Password" -f "/Users/js-15400155/Desktop/FATPMarge-Overlay/Users/gdlocal/Library/Atlas/Resources" -cb "142,FFFFFFFAFFFFFFFBFFFFFFFCFFFFFFFDFFFFFFFE"
atlas-signer -t "/Users/js-15400155/Desktop/FATPMarge-Overlay/Users/gdlocal/Library/Atlas" -p "User Defined Signing Password"
'''

from multiprocessing import Process
from multiprocessing import Queue
import time
import os
import sys, time
import encodings
sys.path.append(os.path.dirname(__file__))
# sys.path.append(os.path.join(os.path.dirname(__file__), "HS_server_django_symple"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/python3.9"))

from HS_client import HS_client # 模块里面必须要有__init__.py， 否则py2app不识别路径
from HS_GUI.HS_login_GUI import  Login_app
from HS_universal.haimeng_log import Log
from HS_server_django_symple import manage


def main():
    logobj = Log(os.path.join(os.path.dirname(__file__), "Resource/HS_tool_log.txt"))
    try:
        logobj.logger.info("开启程序")
        q_sent, q_recv = Queue(10), Queue(10)
        start_client_p = Process(target=HS_client.start_work, args=(q_recv, q_sent, ))
        # start_client_p.daemon = True
        start_client_p.start()
        start_web_p = Process(target=manage.main)
        start_web_p.start()
        Login_app(q_sent, q_recv)
        start_client_p.terminate()
        start_web_p.terminate()
    except Exception as e:
        logobj.logger.info("运行程序出错"+str(e))


if __name__ == "__main__":
    if int(time.localtime()[0])<2023:
        main()