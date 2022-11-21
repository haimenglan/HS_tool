#! /usr/bin/env python3
# -*- coding:utf-8 -*-
#! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import os
import sys,time
import threading
from multiprocessing import Process
import csv
import time
from time import sleep
import re
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import subprocess

import serial  # 导入模块
from serial.tools import list_ports
import traceback

import xlwt
import xlrd
# from haimeng_tk import color_change
# from haimeng_xlwt import Haimeng_xlwt
import find_cmd  # 扣指令工具

# 通用函数
def color_change(r, g, b):
    return "#%02x%02x%02x" % (int(r), int(g), int(b))

class Haimeng_xlwt:
    def __init__(self,file_path=""):
        self.xls_file_path = file_path
        self.xls_book = xlwt.Workbook()
        self.blank_style = self.set_blank_style()

        self.gray_title_style = self.set_style('Helvetica', 250, font_colour=0, font_bold=True, pattern_colour=22)
        self.station_style = self.set_style('Helvetica', 250, font_colour=0, font_bold=True, pattern_colour=67)

        self.normal_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1)
        self.normal_no_wrap_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1,is_wrap=0)
        self.persentage_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1,is_persentage=True)
        self.yellow_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=5)
        self.cyan_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=7)
        self.green_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=3)
        self.orange_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=52)
        self.red_style = self.set_style('Helvetica', 220, font_colour=0, pattern_colour=2, font_bold=False)
        self.blue_style = self.set_style('Helvetica', 220, font_colour=1, pattern_colour=4, font_bold=False)

        self.red_font_style = self.set_style('Helvetica', 220, font_colour=2, font_bold=False,pattern_colour=1)
        self.yellow_font_style = self.set_style('Helvetica', 220, font_colour=52, font_bold=False,pattern_colour=1)

    def set_blank(self,sheet,row_start,row_end,column_start,column_end):
        #print(row_start,row_end,column_start,column_end)
        for i in range(100):
            for j in range(100):
                if i in range(row_start,row_end) and \
                    j in range(column_start,column_end):
                    continue
                else:
                    sheet.write(i,j,"",self.blank_style)

    def set_blank_style(self,pattern_colour=1):
        style = xlwt.XFStyle()  # 新建风格
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置填充模式为全部填充
        pattern.pattern_fore_colour = pattern_colour  # 设置填充颜色为蓝色

        style.pattern = pattern
        return style

    def write_line(self,sheet,row,column,line,style,persent_column=None):
        new_column = column
        for each_value in line:
            if len(str(each_value))>=32767:
                print("can't write too long string: ",str(each_value))
                each_value = each_value[:32767]
            if new_column==0 and style!=self.gray_title_style and each_value!="":
                sheet.write(row,new_column,each_value,self.station_style)
            else:
                if persent_column is not None:
                    if new_column in persent_column:
                        sheet.write(row,new_column,each_value,self.persentage_style)
                    else:
                        sheet.write(row,new_column,each_value,style)
                else:
                    sheet.write(row,new_column,each_value,style)
            new_column += 1

    def set_style(self,font_name, font_height, font_colour=1, font_bold=False,pattern_colour=1,is_wrap=1,is_persentage=False):
        style = xlwt.XFStyle()  # 新建风格
        font = xlwt.Font()  # 新建字体
        font.name = font_name
        font.bold = font_bold  # 是否加粗
        font.colour_index = font_colour
        font.height = font_height
        if is_persentage:
            font.num_format_str = "0.00%"

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置填充模式为全部填充
        pattern.pattern_fore_colour = pattern_colour  # 设置填充颜色为蓝色

        alignment = xlwt.Alignment()  # 创建alignment对齐方式
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        alignment.vert = xlwt.Alignment.VERT_CENTER

        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x00  # 设置左边框线条颜色
        borders.right_colour = 0x00
        borders.top_colour = 0x00
        borders.bottom_colour = 0x00

        style.borders = borders
        style.alignment = alignment
        style.font = font
        style.pattern = pattern
        style.alignment.wrap = is_wrap #是否换行
        return style


class My_serial:
    instance = None
    init_flag = False
    def __new__(cls, dut_bps, time_out, is_GUI = True):  # cls是传入的实例对象
        if cls.instance is None:
            cls.instance = super().__new__(cls)  # 内存空间赋值给类属性，每次都返回这个内存空间
        return cls.instance  # 返回第一次创建对象时的引用, 确保只有一个实例被创建

    def __init__(self, dut_bps, time_out, is_GUI = True):
        if not My_serial.init_flag:
            My_serial.init_flag = True
            # self.root = tk.Toplevel()
            self.all_data = ''
            self.dut_bps = dut_bps
            self.time_out = time_out
            self.port_name = ""
            self.suspend_manully_read = False
            self.quit_manully_read = False
            self.stop_auto_run = False
            self.history_command_list = []
            self.current_command_index = 0
            self.current_mode = ''

            self.is_GUI = is_GUI
            if is_GUI:
                self.init_GUI()
                self.reflesh_port()
                self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)
                self.root.mainloop()
            else:
                self.reflesh_port()

    #***********************************************************************
    #                           GUI 初始化
    #***********************************************************************
    def init_GUI(self):
        self.root = tk.Tk()
        self.root.title("机台通讯")
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.width, self.height = int(self.screenwidth*0.5),int(self.screenheight*0.6)
        self.root.geometry('%sx%s' % (self.width, self.height))

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.grid(row=0, column=0,sticky="wnse")
        self.progress_frame.columnconfigure(1, weight=1)

        self.progress_label = tk.Label(self.progress_frame, text="当前文件 进度：")
        self.progress_label.grid(row=0, column=0,sticky="w")
        style = ttk.Style()
        style.configure("TProgressbar", foreground="blue", background="blue")
        self.progress_bar = ttk.Progressbar(self.progress_frame, maximum=100, value=0, style="TProgressbar")
        self.progress_bar.grid(row=0, column=1, sticky="we",padx=5)

        self.text_DUT = tk.Text(self.root,
                            bg=color_change(20, 20, 20),
                            fg="white",
                            highlightbackground=color_change(250, 250, 250),
                            highlightcolor=color_change(250, 250, 250),
                            highlightthickness=0,
                            borderwidth=0)
        self.text_DUT.grid(row=1, column=0, columnspan = 2,sticky="nswe")
        self.init_text_color()
        self.text_see_end_flag = True
        self.text_DUT.bind("<Enter>",self.not_see_end_text)
        self.text_DUT.bind("<Leave>",self.see_end_text)
        self.entry_DUT_ft = tkFont.Font(family='微软雅黑', size=13)
        self.entry_DUT = tk.Entry(self.root,font=self.entry_DUT_ft)
        self.entry_DUT.grid(row=2, column=0,columnspan = 2, sticky="we")
        self.entry_DUT.bind("<KeyPress-Up>", self.press_kp_up)
        self.entry_DUT.bind("<KeyPress-Down>", self.press_kp_down)

    def press_kp_up(self,event=None):
        if len(self.history_command_list)>0:
            self.current_command_index += 1
            self.entry_DUT.delete(0, tk.END)
            if (len(self.history_command_list) - self.current_command_index)<0:
                self.current_command_index = 1
            self.entry_DUT.insert(0,self.history_command_list[len(self.history_command_list)-self.current_command_index])

    def press_kp_down(self,event=None):
        if len(self.history_command_list)>0:
            self.current_command_index -= 1
            self.entry_DUT.delete(0, tk.END)
            if self.current_command_index<=0:
                self.current_command_index = len(self.history_command_list)
            self.entry_DUT.insert(0,self.history_command_list[len(self.history_command_list)-self.current_command_index])

    def close_GUI(self):
        My_serial.init_flag = False
        self.quit_manully_read = True
        sleep(0.2)
        try:
            self.ser.close()
            print('close port suscess!')
        except Exception as e:
            print('not open port or close failed', e)
        #sys.exit(0)
        self.root.destroy()

    def init_text_color(self):
        self.text_DUT_ft = tkFont.Font(family='微软雅黑', size=13)
        # 发送指令颜色
        self.text_DUT.tag_add("yellow", tk.END)
        self.text_DUT.tag_config("yellow", foreground="yellow", font=self.text_DUT_ft)
        self.text_DUT.tag_add("blue", tk.END)
        self.text_DUT.tag_config("blue", foreground="blue", font=self.text_DUT_ft)
        # 标记符号:)颜色
        self.text_DUT.tag_add("cyan", tk.END)
        self.text_DUT.tag_config("cyan", foreground="cyan", font=self.text_DUT_ft)
        # 报错信息颜色
        self.text_DUT.tag_add("red", tk.END)
        self.text_DUT.tag_config("red", foreground='red', font=self.text_DUT_ft)
        # 连接成功颜色
        self.text_DUT.tag_add("green", tk.END)
        self.text_DUT.tag_config("green", foreground=color_change(120, 248, 90), font=self.text_DUT_ft)
        # 串口列表颜色
        self.text_DUT.tag_add("orange", tk.END)
        self.text_DUT.tag_config("orange", foreground='orange', font=self.text_DUT_ft)
        # 基本颜色
        self.text_DUT.tag_add("white", tk.END)
        self.text_DUT.tag_config("white", foreground='white', font=self.text_DUT_ft)

    def parse_color(self, string, color):
        if color == "yellow":
            string = "\033[1;33m%s\033[0m"%(string)
        elif color == "blue":
            string = "\033[1;34m%s\033[0m"%(string)
        elif color == "cyan":
            string = "\033[1;36m%s\033[0m"%(string)
        elif color == "red":
            string = "\033[1;31m%s\033[0m"%(string)
        elif color == "green":
            string = "\033[1;32m%s\033[0m"%(string)
        elif color == "orange":
            string = "\033[1;35m%s\033[0m"%(string)
        return string

    def not_see_end_text(self,event):
        if self.text_see_end_flag:
            self.text_see_end_flag = False

    def see_end_text(self,event):
        if not self.text_see_end_flag:
            self.text_see_end_flag = True

    #***********************************************************************
    #                           输入输出模块
    #***********************************************************************
    def insert_text_DUT(self, index, data, tag):
        save_path = os.path.join(os.path.expanduser("~"), "Desktop/DUT_communication_output.txt")
        with open(save_path, "a", encoding="utf-8") as f:
            f.write(data)
        if self.is_GUI:
            self.all_data += data
            if len(self.all_data)>1024*1024*200: # 200k
                self.text_DUT.delete('1.0',tk.END)
                self.all_data = ""
            self.text_DUT.insert(index,data,tag)
            if self.text_see_end_flag:
                self.text_DUT.see(tk.END)
        else:
            print(self.parse_color(data, tag), end='', flush=True)

    def print_help(self):
        self.insert_text_DUT(tk.END, "Read me\n", 'green')
        self.insert_text_DUT(tk.END, "input 'q': quit/back\ninput 'superos‘: change diags to os\ninput 'superdiags': change os to diags\n", 'green')
        self.insert_text_DUT(tk.END, "input 'dl' in diags mode to read bettery percent", 'green')

    def entry_DUT_bind(self, string, bind_unbind, key, function=None):
        if self.is_GUI:
            if bind_unbind:
                self.entry_DUT.insert(0, string)
                self.entry_DUT.bind(key, function)
            else:
                self.entry_DUT.unbind(key)
                result = self.entry_DUT.get()
                self.entry_DUT.delete(0,tk.END)
                return result
        else:
            if bind_unbind:
                function()
            else:
                return input('\033[1;36m%s\033[0m '%(string))

    #***********************************************************************
    #                           开始
    #***********************************************************************
    def reflesh_port(self):
        if self.is_GUI:
            self.text_DUT.delete('1.0',tk.END)
        self.print_help()
        self.port_list = list(list_ports.comports()) # 获取端口列表
        self.port_list = [i[0] for i in self.port_list]
        if len(self.port_list) <= 0:
            self.insert_text_DUT(tk.END, "no port found(找不到任何串口设备)\n", 'red')
        else:
            self.insert_text_DUT(tk.END, "usb port list\n", 'blue')
            i = 0
            for each_port in self.port_list:
                self.insert_text_DUT(tk.END, "(" +str(i)+")  "+str(each_port)+"\n", 'cyan')
                i+=1
            self.insert_text_DUT(tk.END, '(' + str(i) + ')  ' + "reflesh port(刷新端口)" + "\n", 'cyan')
            self.insert_text_DUT(tk.END, '(' + str(i+1) + ')  ' + "从UART.log扣command"+"\n", 'cyan')
            self.entry_DUT_bind("select a port to open: ", True, "<KeyPress-Return>", self.select_port)

    def select_port(self, event=None):
        select_num = self.entry_DUT_bind("select a port to open: ", False, "<KeyPress-Return>")
        user_select_port_re = re.search(r'\d+', select_num)  # 匹配数字
        if user_select_port_re != None:
            if int(user_select_port_re.group()) == len(self.port_list):
                self.reflesh_port()
            elif int(user_select_port_re.group()) == len(self.port_list)+1:
                self.find_command()
            elif int(user_select_port_re.group()) < len(self.port_list):
                original_port_name = self.port_list[int(user_select_port_re.group())]  # 原始端口名
                port_name_re = re.search(r'(/dev/cu.+) - ', str(original_port_name))  # 匹配端口名
                self.port_name = original_port_name if port_name_re is None else port_name_re.group(1)  # 最终端口名
                self.insert_text_DUT(tk.END, "you selected port: %s\n"%(self.port_name), 'blue')
                # ----------------触发打开端口名--------------------------------
                self.retry_open_times = 0
                self.open_port()
            else:
                self.insert_text_DUT(tk.END, "input error, must include a number...input again\n", 'red')
                self.entry_DUT_bind("select a port to open: ", True, "<KeyPress-Return>", self.select_port)  
        else:
            self.insert_text_DUT(tk.END, "input error, must include a number...input again\n", 'red')
            self.entry_DUT_bind("select a port to open: ", True, "<KeyPress-Return>", self.select_port)     

    def open_port(self):
        try:
            self.ser = serial.Serial(self.port_name, self.dut_bps, timeout=self.time_out)
        except Exception as e:
            print("打开串口失败",str(e))
        if self.ser.isOpen(): # check open status
            self.retry_open_times = 0
            self.insert_text_DUT(tk.END, "open success!\n", 'green')
            self.current_mode = self.check_current_mode()
            self.insert_text_DUT(tk.END, "current mode is: %s\n"%(self.current_mode), "green")
            self.insert_text_DUT(tk.END, "1)Manually send command(默认手动模式)\n" +
                                 "2)Auto run commnand(自动模式)\n"+
                                 "3)reflesh port(刷新端口)\n"+
                                 "4)从UART.log扣command\n", 'yellow')
            self.entry_DUT_bind("select a function: ", True, "<KeyPress-Return>", self.select_function) 
        else:
            if self.retry_open_times < 20:
                self.retry_open_times += 1
                self.open_port()
            else:  # 尝试打开20+次都失败，要求重新选择
                self.insert_text_DUT(tk.END, "open port failed!\n", 'red')
                self.entry_DUT_bind("select a port to open: ", True, "<KeyPress-Return>", self.select_port)  

    def select_function(self, event=None):
        function_select = self.entry_DUT_bind("select mode:", False, "<KeyPress-Return>")
        user_select_re = re.search(r'\d+', function_select)  # 匹配数字
        if user_select_re != None:
            if int(user_select_re.group())==1:
                self.quit_manully_read = False 
                self.insert_text_DUT(tk.END, "this is mannually mode\n", 'white')
                self.manually_read_thread = threading.Thread(target=self.read_manual_mode_data)
                self.manually_read_thread.setDaemon(True)
                self.manually_read_thread.start()
                self.entry_DUT_bind("", True, "<KeyPress-Return>", self.manually_sent_command)  
            elif int(user_select_re.group())==2:
                self.insert_text_DUT(tk.END, "this is auto mode\n", 'white')
                self.quit_manully_read = True  # 退出手动接受线程
                self.auto_mode_thread = threading.Thread(target=self.start_auto_mode)
                self.auto_mode_thread.setDaemon(True)
                self.auto_mode_thread.start()
                self.entry_DUT_bind("", True, "<KeyPress-Return>", self.auto_sent_command) 
            elif int(user_select_re.group()) == 3:
                self.reflesh_port()
            elif int(user_select_re.group()) == 4:
                self.find_command()
            else:
                self.insert_text_DUT(tk.END, "input error! please try again\n", 'red')
                self.entry_DUT_bind("select a function: ", True, "<KeyPress-Return>", self.select_function) 
        else:
            self.insert_text_DUT(tk.END, "input error! please try again\n", 'red')
            self.entry_DUT_bind("select a function: ", True, "<KeyPress-Return>", self.select_function) 

    #***********************************************************************
    #                             读写数据
    #***********************************************************************   
    def print_data(self,recv_data):
        if ":-)" in recv_data or "root#" in recv_data:
            if "\n" in recv_data:
                search_key = re.search(r"\n.*$",recv_data)
                self.insert_text_DUT(tk.END,"%s"%(recv_data[:search_key.start()]),"white")
                self.insert_text_DUT(tk.END,"%s"%(recv_data[search_key.start():]),"orange")
            else:
                if "error" in str(recv_data) or "ERROR" in str(recv_data):                   
                    self.insert_text_DUT(tk.END,"%s"%(recv_data),"red")
                elif  "warning" in str(recv_data) or "WARNING" in str(recv_data):                   
                    self.insert_text_DUT(tk.END,"%s"%(recv_data),"yellow")
                else:
                    self.insert_text_DUT(tk.END,"%s"%(recv_data),"white")
        else:
            if "error" in str(recv_data) or "ERROR" in str(recv_data):                   
                self.insert_text_DUT(tk.END,"%s"%(recv_data),"red")
            elif "warning" in str(recv_data) or "WARNING" in str(recv_data):                   
                self.insert_text_DUT(tk.END,"%s"%(recv_data),"yellow")
            else:
                self.insert_text_DUT(tk.END,"%s"%(recv_data),"white")
        sleep(0.01) # 防止数据太多刷新太快 text卡顿不显示

    def recv_port_data(self):
        re_connect_time = 0
        recv_data = ""
        while re_connect_time<20:
            try:
                recv_data = self.ser.read(self.ser.in_waiting)
                break
            except Exception as e:
                if ('Device not configured' in str(e) or "argument must be an int" in str(e)):
                    try:
                        self.reconnect_port()
                        break # 如果正常执行表示重连接成功
                    except Exception as e2:
                        re_connect_time += 1
                        if re_connect_time==19:
                            self.insert_text_DUT(tk.END,"重新连接失败:"+str(e2),"red")
                            return None
                elif "device reports readiness to read but returned no data" in str(e):
                    re_connect_time += 1
                    self.quit_manully_read = True
                else:
                    self.insert_text_DUT(tk.END,str(e),"red")
                    re_connect_time += 1
            sleep(0.05)
        try:
            recv_data = recv_data.decode()  # 逐个获取原始 输出字符串
        except:
            try:
                recv_data = recv_data.decode("utf-8-sig")
            except Exception as e:
                self.insert_text_DUT(tk.END,"数据解码异常, 检查波特率是否正确\n"+str(recv_data),"red")
                recv_data = str(recv_data)
        return str(recv_data)

    def read_all_data(self):
        auto_recv_data = ""
        current_time = time.time()
        pass_time = time.time() - current_time
        key_list = [r":-\) $", r"root# "]
        search_end_key = None
        timeout = 100
        if self.current_mode!="diags" and self.current_mode!="os":
            timeout = 1
        while search_end_key is None and pass_time<timeout:
            # if self.stop_auto_run:
            #     break
            for each_key in key_list:
                search_end_key = re.search(each_key,auto_recv_data)
                if search_end_key is not None:
                    break
            pass_time = time.time() - current_time
            recv_data = self.recv_port_data()
            if recv_data is None:
                self.reflesh_port()
                break
            self.print_data(recv_data)
            #self.login_os(recv_data)
            auto_recv_data += str(recv_data)
            recv_data = ""
            sleep(0.02)
        auto_recv_data = self.change_str(auto_recv_data)
        return auto_recv_data

    def write_ser(self,command):
        try:
            sent_command = str(command)
            while len(sent_command)>100:
                self.ser.write(sent_command[:100].encode())
                current_time=time.time()
                while self.ser.out_waiting and (time.time()-current_time)<10:  #10秒钟超时
                    time.sleep(0.05)
                sent_command = sent_command[100:]
            if len(sent_command)!=0:
                current_time=time.time()
                self.ser.write(sent_command.encode())
                while self.ser.out_waiting and (time.time()-current_time)<10: # 当self.ser.out_waiting=False, 表示发送完成
                    time.sleep(0.05)
            self.ser.write("\n".encode())
        except Exception as e:
            print("\033[1;31m写入异常:\033[0m", e)

    #***********************************************************************
    #                             手动模式
    #***********************************************************************
    def login_os(self,respond):
        if "login:" in str(respond):
            self.ser.write('root\n'.encode("utf-8"))
            self.ser.flush()
            sleep(0.05)
            self.ser.write('alpine\n'.encode("utf-8"))
            self.ser.flush()

    def read_manual_mode_data(self):
        while True:
            sleep(0.002)  # 防止界面程序因为多线程卡顿
            if self.quit_manully_read:
                break
            if not self.suspend_manully_read:
                recv_data = self.recv_port_data()
                if recv_data is None:  #重连失败
                    self.reflesh_port()
                    break
                self.login_os(recv_data)
                self.print_data(recv_data)

    def fast_command(self,command):
        if command == "superdiags" or command == "superos":
            self.change_to_diags_os(command)
        elif command == "dl" or command == "DL":
            if self.current_mode=="diags":
                self.write_ser('device -k gasgauge -p\n')
        elif command == 'gj' or command == 'GJ':
            if self.current_mode=="diags":
                self.write_ser('shutdown\n')
        else:
            self.write_ser(command)

    def manually_sent_command(self,event=None):
        command = self.entry_DUT_bind("", False, "")
        if command == "q":   
            self.quit_manully_read = True
            self.open_port()
        self.history_command_list.append(command)
        if len(self.history_command_list) > 100:
            self.history_command_list.pop(0)
        if self.current_command_index !=0:
            self.current_command_index = 0
        self.fast_command(command)
        if not self.is_GUI and not self.quit_manully_read:
            self.manually_sent_command()

    #***********************************************************************
    #                             自动模式
    #***********************************************************************
    def auto_sent_command(self,event=None):
        time.sleep(0.1)
        command = self.entry_DUT_bind("", False, "")
        if command=="q":
            self.stop_auto_run = True
        if not self.stop_auto_run:
            self.auto_sent_command() 
        else:
            self.open_port()

    def read_file(self,file_path):
        file_command_list = []
        if ".csv" in file_path:
            with open(file_path) as csvf:
                read_csv = csv.reader(csvf)
                read_csv = list(read_csv)
                for each_line in read_csv:
                    if each_line!=[]:
                        for each_command in each_line:
                            if "\ufeff" in each_command:
                                each_command=each_command.replace("\ufeff","")
                            file_command_list.append(each_command)
        elif ".xls" in file_path or ".xlsx" in file_path:
            xls_book = xlrd.open_workbook(file_path)
            for each_table in range(1):
                table = xls_book.sheets()[each_table]
                file_command_list = table.col_values(0, 0) #column=0, start_row=0
        return file_command_list

    def start_auto_mode(self):
        self.stop_auto_run = False
        if not self.current_mode:
            self.current_mode = self.check_current_mode()
        try:
            if self.is_GUI:
                all_file_path = tkfile.askopenfilenames(title="choose csv/xls command files(可选多个文件)")
            else:
                all_file_path = input("\033[1;36minput csv/xls command file(use ',' to separate them if you have more than one file): \033[0m").split(",")
            file_num = 0
            for each_file in all_file_path:
                string = ''
                file_num += 1
                file_path = change_path(each_file)
                print("文件路径是", file_path)
                file_name = os.path.basename(each_file)
                file_command_list = self.read_file(file_path)
                auto_result_list = []
                command_num=0
                if self.is_GUI:
                    self.progress_bar["value"] = 0
                for each_command in file_command_list:
                    if self.stop_auto_run:
                        break
                    if each_command!="":
                        self.write_ser(each_command)
                        auto_recv_data = self.read_all_data()
                        auto_result_list.append(auto_recv_data)
                        command_num += 1
                        if self.is_GUI:
                            self.progress_label["text"] = "当前文件(%s/%s) %s 进度：%s/%s" % (file_num,len(all_file_path),
                                                                        file_name, command_num, len(file_command_list))
                            self.progress_bar["value"] = command_num / len(file_command_list) * 100
                        # else:
                        #     if command_num%10==0:
                        #         string = f"\nfile progress: {file_num}/{len(all_file_path)}, command progress: {command_num}/{len(file_command_list)} "
                        #         print(string, end="", flush=True)
                self.insert_text_DUT(tk.END, "\nfile '%s' running finished! %d command been sent, "%(file_path,len(auto_result_list)), 'green')
                if auto_result_list!=[]:
                    self.save_xls(auto_result_list,file_path)
        except Exception as e:
            print("auto run error",str(e))
        # self.open_port()
        self.stop_auto_run = True

    def save_xls(self,auto_result_list,file_path):
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path) # 获取FATP_Marge.csv
        file_name = os.path.splitext(file_name)[0] # 获取FATP_Marge
        save_path = os.path.join(path,file_name+"_result.xls")  
        result_num = 0

        haimeng_xlwt = Haimeng_xlwt(save_path)
        sheet = haimeng_xlwt.xls_book.add_sheet("result")
        summary_sheet = haimeng_xlwt.xls_book.add_sheet("summary")
        # 写标题，设置列宽
        title = ["command","result",""]
        for i in [sheet, summary_sheet]:
            haimeng_xlwt.write_line(i, 0, 0, title, haimeng_xlwt.gray_title_style)
            i.col(0).width, i.col(1).width, i.col(2).width = 10000, 20000, 20000
        row = 1
        summary_row = 1
        summary_command_l = []
        for each_result in auto_result_list:
            result_num += 1
            # 搜索command
            command_re = re.search(r"^(.+)\n",each_result)
            result_start = 0
            if command_re!=None:
                result_start = command_re.end()
                command = each_result[:command_re.end()-1]
            else:
                command = each_result
            # 按diags模式搜索结果
            respond_re = re.search(r"\r*\n*\[.+\].:-\)",each_result)
            if respond_re is None:
                # 按os模式查找结果
                respond_re = re.search(r"\r*\n*.*:~ root#", each_result)
            if respond_re is not None:
                result = each_result[result_start:respond_re.start()]
            else:
                result = each_result
            # 判断结果颜色
            if 'WARNING' in result and 'ERROR' not in result and "error" not in result:
                color = haimeng_xlwt.yellow_font_style
            elif 'ERROR' in result or "error" in result:
                color = haimeng_xlwt.red_font_style
            else:
                color = haimeng_xlwt.normal_style
            result_list = []
            while len(str(result))>32760:  #大于这个长度写不进一个单元格
                result_list.append(result[:32760])
                result = result[32760:]
            if len(str(result))>0:
                result_list.append(result)
            # 写入command
            sheet.write(row,0,command,haimeng_xlwt.normal_style) 
            if command not in summary_command_l and color!=haimeng_xlwt.normal_style:
                summary_sheet.write(summary_row, 0, command, haimeng_xlwt.normal_style) 
            result_column = 1
            # 写入结果
            for each_column in result_list:
                sheet.write(row,result_column,each_column,color)
                if command not in summary_command_l and color!=haimeng_xlwt.normal_style:
                    summary_sheet.write(summary_row, result_column, each_column, color)
                result_column += 1
            row+=1
            if command not in summary_command_l and color!=haimeng_xlwt.normal_style:
                summary_row += 1
                summary_command_l.append(command)
        # 保存文件，提示
        haimeng_xlwt.xls_book.save(save_path)
        self.insert_text_DUT(tk.END,"%d command been readed.\n"%(result_num),"green")
        self.insert_text_DUT(tk.END,"result have saved at %s\n"%(save_path),"green")

    #***********************************************************************
    #                             unit.log 扣command
    #***********************************************************************
    def find_command(self):
        if self.is_GUI:
            path = tkfile.askopenfilename(title="选择uart.log文件")
            save_path = tkfile.asksaveasfilename(title="选择保存位置和名称", defaultextension=".csv")
        else:
            path = change_path(input(self.parse_color("input UART.log file", "cyan")))
            save_path = os.path.join(os.path.dirname(path), "UART_command.csv")
        find_cmd.main(path, save_path, self.insert_text_DUT)
        self.insert_text_DUT(tk.END, "result have saved at %s\n" % (save_path), "green")
        self.reflesh_port()


    #***********************************************************************
    #                             其它
    #***********************************************************************
    def change_str(self,string):
        # ---移除控制终端颜色的字符
        while ("\033[" in string):
            search_key = re.search('\033(\[\d{1,3}m){1,3}', string)
            if search_key != None:
                string = string.replace(search_key.group(), '')
            else:
                break
        return string

    def reconnect_port(self):
        self.ser.close()
        print("\033[1;31m设备连接不稳定,尝试重连\033[0m")
        self.ser = serial.Serial(self.port_name, self.dut_bps, timeout=self.time_out)
        print("\033[1;32m重新连接成功...\033[0m") #处理Device not configured异常

    def check_current_mode(self):
        self.suspend_manully_read = True  # 暂停接收
        current_mode = ""
        self.write_ser("")
        self.write_ser("")
        recv_data = self.read_all_data()
        if ":-)" in recv_data:
            current_mode = "diags"
        elif "root#" in recv_data:
            current_mode = "os"
        elif "]" in recv_data:
            current_mode = "recovery"
        self.current_mode = current_mode
        self.suspend_manully_read = False
        return current_mode

    def change_to_diags_os(self,command):
        self.current_mode = self.check_current_mode()
        os_to_diags_command_list = ["nvram boot-command=diags","nvram auto-boot=true",  "reboot"]
        diags_to_os_command_list = ["nvram --set boot-command 'fsboot'",
                                            "nvram --set auto-boot 'true'", "nvram --save", "reset"]
        if command == "superdiags":
            if self.current_mode == "diags":
                self.insert_text_DUT(tk.END,"you already in diags","yellow")
            elif self.current_mode == "os":
                for each_command in os_to_diags_command_list:
                    self.write_ser(each_command)
            elif self.current_mode == "recovery":
                self.write_ser("diags")
            else:
                self.insert_text_DUT(tk.END,"not support this command in this mode %s"%(self.current_mode),"yellow")
        elif command == "superos":
            if self.current_mode == "os":
                self.insert_text_DUT(tk.END,"you already in os","yellow")
            elif self.current_mode == "diags":
                for each_command in diags_to_os_command_list:
                    self.write_ser(each_command)
            else:
                self.insert_text_DUT(tk.END,"not support this command in this mode: %s"%(self.current_mode),"yellow")


# 给出新旧command文件，自动模式下，当跑到的command在旧command列表中，则下一条指令执行新command
# sumamry表格给出新旧command结果对比
class My_serial_for_new_cmd(My_serial):
    def __new__(cls, dut_bps, time_out, is_GUI=True, new_old_path=''):
        return super().__new__(cls, dut_bps,time_out, is_GUI)

    def __init__(self, dut_bps, time_out, is_GUI=True, new_old_path=''):
        if new_old_path:
            self.old_cmd, self.new_cmd= self.get_new_old_cmd(new_old_path)
        else:
            self.old_cmd, self.new_cmd= [], []
        # print("old command++++++++++++++++", self.old_cmd)
        # print("new command++++++++++++++++", self.new_cmd)
        super().__init__(dut_bps,time_out, is_GUI)


    def get_new_old_cmd(self, path):
        excelbook = xlrd.open_workbook(path)
        sheet = excelbook.sheet_by_index(0)
        old_cmd = sheet.col_values(0)
        new_cmd = sheet.col_values(1)
        old_cmd2, new_cmd2 = [],[]
        for i, cmd in enumerate(old_cmd):
            if new_cmd[i] != '':
                old_cmd2.append(cmd)
                new_cmd2.append(new_cmd[i])
        return old_cmd2, new_cmd2

    def start_auto_mode(self):
        self.stop_auto_run = False
        try:
            if self.is_GUI:
                all_file_path = tkfile.askopenfilenames(title="choose csv/xls command files(可选多个文件)")
            else:
                all_file_path = input("\033[1;36minput csv/xls command file(use ',' to separate them if you have more than one file): \033[0m").split(",")
            file_num = 0
            for each_file in all_file_path:
                file_num += 1
                file_path = change_path(each_file)
                file_name = os.path.basename(each_file)
                file_command_list = self.read_file(file_path)
                auto_result_list = []
                command_num=0
                if self.is_GUI:
                    self.progress_bar["value"] = 0
                for each_command in file_command_list:
                    if self.stop_auto_run:
                        break
                    if each_command!="":
                        self.write_ser(each_command)
                        auto_recv_data = self.read_all_data()
                        auto_result_list.append(auto_recv_data)
                        command_num += 1
                        if self.is_GUI:
                            self.progress_label["text"] = "当前文件(%s/%s) %s 进度：%s/%s" % (file_num,len(all_file_path),
                                                                    file_name, command_num, len(file_command_list))
                            self.progress_bar["value"] = command_num / len(file_command_list) * 100
                    # -------------  比旧的类方法新增内容 --------------
                    if each_command in self.old_cmd:
                        index = self.old_cmd.index(each_command)
                        self.write_ser(self.new_cmd[index])
                        auto_recv_data = self.read_all_data()
                        auto_result_list.append(auto_recv_data)
                    # ----------------------------------------------
                self.insert_text_DUT(tk.END, "\nfile '%s' running finished! %d command been sent, "%(file_path,len(auto_result_list)), 'green')
                if auto_result_list!=[]:
                    self.save_xls(auto_result_list, file_path)
        except Exception as e:
            traceback.print_exc()
            print("auto run error",str(e))
        self.stop_auto_run = True

    def get_color(self, result, haimeng_xlwt):
        if 'WARNING' in result and 'ERROR' not in result and "error" not in result:
            color = haimeng_xlwt.yellow_font_style
        elif 'ERROR' in result or "error" in result:
            color = haimeng_xlwt.red_font_style
        else:
            color = haimeng_xlwt.normal_style
        return color

    def save_xls(self,auto_result_list,file_path):
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path) # 获取FATP_Marge.csv
        file_name = os.path.splitext(file_name)[0] # 获取FATP_Marge
        save_path = os.path.join(path,file_name+"_result.xls")  
        result_num = 0
        haimeng_xlwt = Haimeng_xlwt(save_path)
        sheet = haimeng_xlwt.xls_book.add_sheet("result")
        summary_sheet = haimeng_xlwt.xls_book.add_sheet("summary")
        # 写标题，设置列宽
        title = ["command","result",""]
        for i in [sheet, summary_sheet]:
            haimeng_xlwt.write_line(i, 0, 0, title, haimeng_xlwt.gray_title_style)
            i.col(0).width, i.col(1).width, i.col(2).width = 10000, 20000, 20000
        row = 1
        summary_row = 1
        summary_command_l = []
        result_dict = {}
        for each_result in auto_result_list:
            result_num += 1
            # 搜索command
            command_re = re.search(r"^(.+)\n",each_result)
            result_start = 0
            if command_re!=None:
                result_start = command_re.end()
                command = each_result[:command_re.end()-1]
            else:
                command = each_result
            # 按diags模式搜索结果
            respond_re = re.search(r"\r*\n*\[.+\].:-\)",each_result)
            if respond_re is None:
                # 按os模式查找结果
                respond_re = re.search(r"\r*\n*.*:~ root#", each_result)
            if respond_re is not None:
                result = each_result[result_start:respond_re.start()]
            else:
                result = each_result
            result_dict[command] = result
            # 判断结果颜色
            color = self.get_color(result, haimeng_xlwt)
            result_list = []
            while len(str(result))>32760:  #大于这个长度写不进一个单元格
                result_list.append(result[:32760])
                result = result[32760:]
            if len(str(result))>0:
                result_list.append(result)
            # 写入command
            sheet.write(row,0,command,haimeng_xlwt.normal_style) 
            is_write_summary = False
            if (command not in summary_command_l and color!=haimeng_xlwt.normal_style
                    and command not in self.new_cmd) or command in self.old_cmd:
                is_write_summary = True
                summary_sheet.write(summary_row, 0, command, haimeng_xlwt.normal_style) 
            result_column = 1
            # 写入结果
            for each_column in result_list:
                sheet.write(row,result_column,each_column,color)
                if is_write_summary:
                    summary_sheet.write(summary_row, result_column, each_column, color)
                result_column += 1
            row+=1
            if is_write_summary:
                summary_row += 1
                summary_command_l.append(command)
        # 写入新command 结果
        summary_sheet.write(0, 3, "new command", haimeng_xlwt.gray_title_style) 
        summary_sheet.write(0, 4, "new command result", haimeng_xlwt.gray_title_style) 
        for i, cmd in enumerate(summary_command_l):
            if cmd in self.old_cmd:
                new_cmd = self.new_cmd[self.old_cmd.index(cmd)]
                if new_cmd in result_dict:
                    new_result = result_dict[new_cmd]
                else: 
                    new_result = "not found!"
                color = self.get_color(new_result, haimeng_xlwt)
                summary_sheet.write(i+1, 3, new_cmd, haimeng_xlwt.normal_style) 
                summary_sheet.write(i+1, 4, new_result, color) 
        # 保存文件，提示
        haimeng_xlwt.xls_book.save(save_path)
        self.insert_text_DUT(tk.END,"%d command been read.\n"%(result_num),"green")
        self.insert_text_DUT(tk.END,"result have save at %s\n"%(save_path),"green")


def start_usbfs():
    try:
        path = os.path.join(os.path.expanduser("~"), "HS_tool")
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, "usbfs")
        if not os.path.exists(path):
            os.mkdir(path)
        # print("usbfs 路径",os.path.join(path,"usbfs"))
        # os.system("usbfs -f %s"%(os.path.join(path,"usbfs")))
        # subprocess.run(f"/usr/local/bin/usbfs -f {os.path.join(path,'usbfs')}")
        t = subprocess.Popen(["/usr/local/bin/usbfs", "-f", path], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        print("运行usbfs失败", str(e))


def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while " " == path[0]:
        path = path[1:]
    while "\\" in path:
        path = path.replace("\\","")
    return path

def run_sys_cmd(command):
    try:
        # subprocess.run(command, shell=False)
        t = subprocess.Popen(command.split(" "), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        print("run command %s error"%(command), str(e))


def main(baund_rate, time_out=None, run_usbfs=True, is_GUI=True, new_old_path=''):
    run_sys_cmd("killall -9 usbfs")
    run_sys_cmd("killall -9 nanokdp")   
    if run_usbfs:
        try:
            usbfs_p = threading.Thread(target=start_usbfs)
            # usbfs_p.daemon = True
            usbfs_p.setDaemon(True)
            usbfs_p.start()
        except Exception as e:
            print("启动usbfs失败", str(e))
    if not new_old_path:
        dut_sent_command = My_serial(baund_rate, time_out, is_GUI)
    else:
        dut_sent_command = My_serial_for_new_cmd(baund_rate, time_out, is_GUI, new_old_path)


if __name__ == "__main__":
    main(115200, is_GUI=False, new_old_path='')

        
