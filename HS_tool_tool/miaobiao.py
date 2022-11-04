import threading
import csv
import time
from time import sleep
import re
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import os


class Miaobiao:
    # have_instace = None
    # is_inti = False
    # def __new__(cls,width,height):
    #     if not cls.have_instace:
    #         cls.have_instace = super().__new__(cls)
    #     return cls.have_instace

    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("秒表")
        self.screenwidth,self.screenheight = self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        width, height = int(self.screenwidth * 0.3), int(self.screenheight * 0.15)
        self.root.geometry('%sx%s' % (width,height))
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.text_miaobiao = tk.Text(self.root,bg="black",fg="yellow")
        self.text_miaobiao.grid(row=0,column=0,columnspan=3,sticky="nswe")

        ft = tkFont.Font(family='微软雅黑',size=48)
        self.text_miaobiao.insert(tk.END,"\n")
        self.text_miaobiao.tag_add("miaobiao","2.0")
        self.text_miaobiao.tag_config("miaobiao",foreground='yellow',background='black',font=ft)
        self.display_value = '%02d:%02d:%02d:%03d' % (0, 0, 0, 0)

        self.text_miaobiao.delete('2.0', '2.end')
        self.text_miaobiao.insert('2.0', self.display_value, 'miaobiao')

        self.pass_time = 0
        self.start_flag = False
        self.stop_flag = False

        # self.self.root_tool_frame_dut_button
        self.fun_timer_start_button = tk.Button(self.root, text="开始",command=self.start)
        self.fun_timer_start_button.grid(row=1, column=0, padx=10, pady=5, sticky="we")

        self.fun_timer_stop_button = tk.Button(self.root, text="停止",command=self.stop)
        self.fun_timer_stop_button.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.fun_timer_reset_button = tk.Button(self.root, text="清零",command=self.reset)
        self.fun_timer_reset_button.grid(row=1, column=2, padx=10, pady=5, sticky="we")
        self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)
        self.root.mainloop()

    def close_GUI(self):
        self.start_flag = False
        self.stop_flag = True
        sleep(0.2)
        self.root.destroy()

    def display(self):
        if self.start_flag and not self.stop_flag:
            self.pass_time = time.time() - self.init_time
            self.hour = int(self.pass_time/3600)
            self.min = int(self.pass_time/60 - self.hour*60)
            self.sec = int(self.pass_time - self.hour*3600 - self.min*60)
            self.millisec = int(( self.pass_time - self.hour*3600 - self.min*60 - self.sec) *1000)

            self.display_value = '%02d:%02d:%02d:%03d' %(self.hour, self.min, self.sec, self.millisec)

            self.text_miaobiao.delete('2.0','2.end')
            self.text_miaobiao.insert('2.0',self.display_value,'miaobiao')
        
            self.timer_miaobiao = threading.Timer(0.001, self.display)
            self.timer_miaobiao.setDaemon(True)
            self.timer_miaobiao.start()

    def start(self):
        if self.start_flag:
            pass
            #tkmessage.showinfo("sorry","i am running")
        else:
            self.start_flag = True
            if self.stop_flag:
                self.init_time = time.time() - self.pass_time
                self.stop_flag = False
            else:
                self.init_time = time.time()
            self.timer_miaobiao = threading.Timer(0, self.display)
            self.timer_miaobiao.setDaemon(True)
            self.timer_miaobiao.start() 

    def stop(self):
        self.start_flag = False
        self.stop_flag = True

        
    def reset(self):
        #if self.stop_flag:
        self.stop_flag = True
        self.start_flag = False
        retry = 10
        while(retry>1):
            retry -= 1
            self.millisec,self.sec,self.min,self.hour = 0,0,0,0
            self.display_value = '%02d:%02d:%02d:%03d' %(self.hour, self.min, self.sec, self.millisec)
            #ft = ttk.Font(family='微软雅黑',size=24)
            self.text_miaobiao.delete('2.0','2.end')
            self.text_miaobiao.insert('2.0',self.display_value,'miaobiao')
            #self.text_
        self.stop_flag = False




    
    