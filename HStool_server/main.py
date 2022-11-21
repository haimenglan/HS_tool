import socket
import platform
from multiprocessing import Process
from multiprocessing import Queue
import os
import sys
sys.path.append(os.path.dirname(__file__))
from manager import Manager
import traceback

if __name__ == "__main__":
    # m = Manager("127.0.0.1", 7999)

    m = Manager("192.168.0.103", 7999)
    m.run()