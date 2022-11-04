#! /usr/bin/env python3
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

import serial  # 导入模块
from serial.tools import list_ports

import xlwt
import xlrd
from haimeng_xlwt import Haimeng_xlwt
from haimeng_tk import color_change

# 通用函数
# def color_change(r, g, b):
#     return "#%02x%02x%02x" % (int(r), int(g), int(b))

# class Haimeng_xlwt:
#     def __init__(self,file_path=""):
#         self.xls_file_path = file_path
#         self.xls_book = xlwt.Workbook()
#         self.blank_style = self.set_blank_style()

#         self.gray_title_style = self.set_style('Helvetica', 250, font_colour=0, font_bold=True, pattern_colour=22)
#         self.station_style = self.set_style('Helvetica', 250, font_colour=0, font_bold=True, pattern_colour=67)

#         self.normal_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1)
#         self.normal_no_wrap_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1,is_wrap=0)
#         self.persentage_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1,is_persentage=True)
#         self.yellow_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=5)
#         self.cyan_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=7)
#         self.green_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=3)
#         self.orange_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=52)
#         self.red_style = self.set_style('Helvetica', 220, font_colour=0, pattern_colour=2, font_bold=False)
#         self.blue_style = self.set_style('Helvetica', 220, font_colour=1, pattern_colour=4, font_bold=False)

#         self.red_font_style = self.set_style('Helvetica', 220, font_colour=2, font_bold=False,pattern_colour=1)
#         self.yellow_font_style = self.set_style('Helvetica', 220, font_colour=52, font_bold=False,pattern_colour=1)

#     def set_blank(self,sheet,row_start,row_end,column_start,column_end):
#         #print(row_start,row_end,column_start,column_end)
#         for i in range(100):
#             for j in range(100):
#                 if i in range(row_start,row_end) and \
#                     j in range(column_start,column_end):
#                     continue
#                 else:
#                     sheet.write(i,j,"",self.blank_style)

#     def set_blank_style(self,pattern_colour=1):
#         style = xlwt.XFStyle()  # 新建风格
#         pattern = xlwt.Pattern()
#         pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置填充模式为全部填充
#         pattern.pattern_fore_colour = pattern_colour  # 设置填充颜色为蓝色

#         style.pattern = pattern
#         return style

#     def write_line(self,sheet,row,column,line,style,persent_column=None):
#         new_column = column
#         for each_value in line:
#             if len(str(each_value))>=32767:
#                 print("can't write too long string: ",str(each_value))
#                 each_value = each_value[:32767]
#             if new_column==0 and style!=self.gray_title_style and each_value!="":
#                 sheet.write(row,new_column,each_value,self.station_style)
#             else:
#                 if persent_column is not None:
#                     if new_column in persent_column:
#                         sheet.write(row,new_column,each_value,self.persentage_style)
#                     else:
#                         sheet.write(row,new_column,each_value,style)
#                 else:
#                     sheet.write(row,new_column,each_value,style)
#             new_column += 1

#     def set_style(self,font_name, font_height, font_colour=1, font_bold=False,pattern_colour=1,is_wrap=1,is_persentage=False):
#         style = xlwt.XFStyle()  # 新建风格
#         font = xlwt.Font()  # 新建字体
#         font.name = font_name
#         font.bold = font_bold  # 是否加粗
#         font.colour_index = font_colour
#         font.height = font_height
#         if is_persentage:
#             font.num_format_str = "0.00%"

#         pattern = xlwt.Pattern()
#         pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置填充模式为全部填充
#         pattern.pattern_fore_colour = pattern_colour  # 设置填充颜色为蓝色

#         alignment = xlwt.Alignment()  # 创建alignment对齐方式
#         alignment.horz = xlwt.Alignment.HORZ_LEFT
#         alignment.vert = xlwt.Alignment.VERT_CENTER

#         borders = xlwt.Borders()
#         borders.left = xlwt.Borders.THIN
#         borders.right = xlwt.Borders.THIN
#         borders.top = xlwt.Borders.THIN
#         borders.bottom = xlwt.Borders.THIN
#         borders.left_colour = 0x00  # 设置左边框线条颜色
#         borders.right_colour = 0x00
#         borders.top_colour = 0x00
#         borders.bottom_colour = 0x00

#         style.borders = borders
#         style.alignment = alignment
#         style.font = font
#         style.pattern = pattern
#         style.alignment.wrap = is_wrap #是否换行
#         return style


def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while "\\" in path:
        path = path.replace("\\","")
    return path

def mount_usbfs():
    os.system("killall -9 usbfs")
    os.system("killall -9 nanokdp")
    path = sys.path[0]
    if not os.path.exists(os.path.join(path,"usbfs")):
        os.mkdir(os.path.join(path,"usbfs"))
    print("usbfs 路径",os.path.join(path,"usbfs"))
    os.system("usbfs -f %s"%(os.path.join(path,"usbfs")))

class My_serial:
    instance = None
    init_flag = False
    def __new__(cls,dut_bps,time_out):  # cls是传入的实例对象
        if cls.instance is None:
            usbfs_thread = threading.Thread(target=mount_usbfs)
            usbfs_thread.setDaemon(True)
            usbfs_thread.start()
            sleep(0.1)
            cls.instance = super().__new__(cls)  # 内存空间赋值给类属性，每次都返回这个内存空间
        return cls.instance  # 返回第一次创建对象时的引用, 确保只有一个实例被创建

    def __init__(self,dut_bps,time_out):
        if not My_serial.init_flag:
            My_serial.init_flag = True
            # self.root = tk.Toplevel()
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

            self.dut_bps = dut_bps
            self.time_out = time_out
            self.port_name = ""
            self.suspend_manully_read = False
            self.quit_manully_read = False
            self.stop_auto_run = False
            self.history_command_list = []
            self.current_command_index = 0

            self.reflesh_port()
            self.root.protocol('WM_DELETE_WINDOW', self.close_GUI)
            self.root.mainloop()

    def press_kp_up(self,event):
        if len(self.history_command_list)>0:
            self.current_command_index += 1
            self.entry_DUT.delete(0, tk.END)
            if (len(self.history_command_list) - self.current_command_index)<0:
                self.current_command_index = 1
            self.entry_DUT.insert(0,self.history_command_list[len(self.history_command_list)-self.current_command_index])


    def press_kp_down(self,event):
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

    def not_see_end_text(self,event):
        if self.text_see_end_flag:
            self.text_see_end_flag = False

    def see_end_text(self,event):
        if not self.text_see_end_flag:
            self.text_see_end_flag = True

    def insert_text_DUT(self,index,data,tag):
        try:
            self.text_DUT.insert(index,data,tag)
            if self.text_see_end_flag:
                self.text_DUT.see(tk.END)
        except:
            print(data)

    def print_help(self):
        self.insert_text_DUT(tk.END, "Read me\n", 'green')
        self.insert_text_DUT(tk.END, "input 'q': quit/back\ninput 'superos‘: change diags to os\ninput 'superdiags': change os to diags\n", 'green')

    def reflesh_port(self):
        self.text_DUT.delete('1.0',tk.END)
        self.print_help()
        self.port_list = list(list_ports.comports()) # 获取端口列表
        if len(self.port_list) <= 0:
            self.insert_text_DUT(tk.END, "no port found(找不到任何串口设备)\n", 'red')
        else:
            self.insert_text_DUT(tk.END, "usb port list\n", 'blue')
            i = 0
            for each_port in self.port_list:
                self.insert_text_DUT(tk.END, "(" +str(i)+")  "+str(each_port)+"\n", 'cyan')
                i+=1
            self.insert_text_DUT(tk.END, '(' + str(i) + ')  ' + "reflesh port(刷新端口)"+"\n", 'cyan')
            self.entry_DUT.insert(0,"select a port to open: ")
            self.entry_DUT.bind("<KeyPress-Return>", self.select_port)

    def select_port(self,event):
        self.entry_DUT.unbind("<KeyPress-Return>")
        select_num = self.entry_DUT.get()
        self.entry_DUT.delete(0,tk.END)
        user_select_port_re = re.search(r'\d+', select_num)  # 匹配数字
        if user_select_port_re != None:
            if int(user_select_port_re.group()) == len(self.port_list):
                self.reflesh_port()
            elif int(user_select_port_re.group()) < len(self.port_list):
                original_port_name = self.port_list[int(user_select_port_re.group())]  # 原始端口名
                port_name_re = re.search(r'(/dev/cu.+) - ', str(original_port_name))  # 匹配端口名
                self.port_name = port_name_re.group(1)  # 最终端口名
                self.insert_text_DUT(tk.END, "you selected port: %s\n"%(self.port_name), 'blue')
                # ----------------触发打开端口名--------------------------------
                self.retry_open_times = 0
                self.open_port()
            else:
                self.entry_DUT.insert(0,"select a port to open: ")
                self.entry_DUT.bind("<KeyPress-Return>", self.select_port)
                self.insert_text_DUT(tk.END, "input error, must include a number...input again\n", 'red')
        else:
            self.entry_DUT.insert(0,"select a port to open: ")
            self.entry_DUT.bind("<KeyPress-Return>", self.select_port)
            self.insert_text_DUT(tk.END, "input error, must include a number...input again\n", 'red')

    def open_port(self):
        try:
            self.ser = serial.Serial(self.port_name, self.dut_bps, timeout=self.time_out)
        except Exception as e:
            print("打开串口失败",str(e))
        if self.ser.isOpen(): # check open status
            self.insert_text_DUT(tk.END, "open success\n", 'green')
            self.insert_text_DUT(tk.END, "1)Manually send command(默认手动模式)\n2)Auto run diags commnand(自动模式)\n3)reflesh port(刷新端口)\n", 'yellow')
            self.entry_DUT.insert(0,"select a function: ")
            self.entry_DUT.bind("<KeyPress-Return>", self.select_function)
        else:
            if self.retry_open_times < 20:
                self.retry_open_times += 1
                self.open_port()
            else:  # 尝试打开20+次都失败，要求重新选择
                self.insert_text_DUT(tk.END, "open port failed!\n", 'red')
                self.entry_DUT.insert(0,"select a port to open: ")
                self.entry_DUT.bind("<KeyPress-Return>", self.select_port)

    def select_function(self,event):
        self.entry_DUT.unbind("<KeyPress-Return>")
        function_select = self.entry_DUT.get()
        self.entry_DUT.delete(0,tk.END)
        user_select_re = re.search(r'\d+', function_select)  # 匹配数字
        if user_select_re != None:
            if int(user_select_re.group())==1:
                self.quit_manully_read = False 
                self.insert_text_DUT(tk.END, "this is mannually mode\n", 'white')
                self.manually_read_thread = threading.Thread(target=self.read_manual_mode_data)
                self.manually_read_thread.setDaemon(True)
                self.manually_read_thread.start()
                self.entry_DUT.bind("<KeyPress-Return>", self.manually_sent_command)
            elif int(user_select_re.group())==2:
                self.insert_text_DUT(tk.END, "this is auto mode\n", 'white')
                self.quit_manully_read = True  # 退出手动接受线程
                self.auto_mode_thread = threading.Thread(target=self.start_auto_mode)
                self.auto_mode_thread.setDaemon(True)
                self.auto_mode_thread.start()
                self.entry_DUT.bind("<KeyPress-Return>", self.auto_sent_command)
            elif int(user_select_re.group())==3:
                self.reflesh_port()
            else:
                self.insert_text_DUT(tk.END, "input error! please try again\n", 'red')
                self.entry_DUT.insert(0,"select a function: ")
                self.entry_DUT.bind("<KeyPress-Return>", self.select_function)
        else:
            self.insert_text_DUT(tk.END, "input error! please try again\n", 'red')
            self.entry_DUT.insert(0,"select a function: ")
            self.entry_DUT.bind("<KeyPress-Return>", self.select_function)


    def login_os(self,respond):
        if "login:" in str(respond):
            self.ser.write('root\n'.encode("utf-8"))
            self.ser.flush()
            sleep(0.05)
            self.ser.write('alpine\n'.encode("utf-8"))
            self.ser.flush()

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

    def reconnect_port(self):
        self.ser.close()
        print("\033[1;31m设备连接不稳定,尝试重连\033[0m")
        self.ser = serial.Serial(self.port_name, self.dut_bps, timeout=self.time_out)
        print("\033[1;32m重新连接成功...\033[0m") #处理Device not configured异常

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
            recv_data = recv_data.decode("utf-8")  # 逐个获取原始 输出字符串
        except:
            try:
                recv_data = recv_data.decode("utf-8-sig")
            except Exception as e:
                self.insert_text_DUT(tk.END,"数据解码异常:"+str(e),"red")
        return str(recv_data)

    def change_str(self,string):
        # ---移除控制终端颜色的字符
        while ("\033[" in string):
            search_key = re.search('\033(\[\d{1,3}m){1,3}', string)
            if search_key != None:
                string = string.replace(search_key.group(), '')
            else:
                break
        return string

    def read_all_data(self):
        auto_recv_data = ""
        current_time = time.time()
        pass_time = time.time() - current_time
        key_list = [r":-\) $", r"root# "]
        search_end_key = None
        while search_end_key is None and pass_time<100:
            if self.stop_auto_run:
                break
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
            
    def check_current_mode(self):
        current_mode = ""
        self.write_ser("")
        recv_data = self.read_all_data()
        if ":-)" in recv_data:
            current_mode = "diags"
        elif "root#" in recv_data:
            current_mode = "os"
        elif "]" in recv_data:
            current_mode = "recovery"
        return current_mode

    def change_to_diags_os(self,command):
        os_to_diags_command_list = ["nvram boot-command=diags","nvram auto-boot=true",  "reboot"]
        diags_to_os_command_list = ["nvram --set boot-command 'fasboot'", 
                                            "nvram --set auto-boot 'true'", "nvram --save", "reset"]
        current_mode = self.check_current_mode()
        if command == "superdiags":
            if current_mode == "diags":
                self.insert_text_DUT(tk.END,"you already in diags","yellow")
            elif current_mode == "os":
                for each_command in os_to_diags_command_list:
                    self.write_ser(each_command)
        elif command == "superos":
            if current_mode == "os":
                self.insert_text_DUT(tk.END,"you already in os","yellow")
            elif current_mode == "diags":
                for each_command in diags_to_os_command_list:
                    self.write_ser(each_command)

    def fast_command(self,command):
        if command == "q":   
            self.quit_manully_read = True
            self.open_port()
        elif command == "superdiags" or command == "superos":
            self.change_to_diags_os(command)
        elif command == "dl" or command == "DL":
            self.write_ser('device -k gasgauge -p\n')
        elif command == 'gj' or command == 'GJ':
            self.write_ser('shutdown\n')
        else:
            self.write_ser(command)

    def manually_sent_command(self,event):
        command = self.entry_DUT.get()
        self.entry_DUT.delete(0,tk.END)
        self.history_command_list.append(command)
        
        if len(self.history_command_list) > 100:
            self.history_command_list.pop(0)
        if self.current_command_index !=0:
            self.current_command_index = 0

        self.suspend_manully_read = True  # 暂停手动接收线程
        self.fast_command(command)
        self.suspend_manully_read = False

    def auto_sent_command(self,event):
        command = self.entry_DUT.get()
        if command=="q":
            self.stop_auto_run = True

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
        print("start auto")
        try:
            all_file_path = tkfile.askopenfilenames(title="choose csv/xls command files(可选多个文件)")
            file_num = 0
            for each_file in all_file_path:
                file_num += 1
                file_path = change_path(each_file)
                file_name = os.path.basename(each_file)
                file_command_list = self.read_file(file_path)
                auto_result_list = []
                command_num=0
                self.progress_bar["value"] = 0
                for each_command in file_command_list:
                    if self.stop_auto_run:
                        break
                    if each_command!="":
                        self.write_ser(each_command)
                        auto_recv_data = self.read_all_data()
                        auto_result_list.append(auto_recv_data)
                        command_num += 1
                        self.progress_label["text"] = "当前文件(%s/%s) %s 进度：%s/%s" % (file_num,len(all_file_path),
                                                                    file_name, command_num, len(file_command_list))
                        self.progress_bar["value"] = command_num / len(file_command_list) * 100

                self.insert_text_DUT(tk.END, "\nfile '%s' running finished! %d command been sent, "%(file_path,len(auto_result_list)), 'green')
                if auto_result_list!=[]:
                    self.save_xls(auto_result_list,file_path)
        except Exception as e:
            print("auto run error",str(e))
        self.open_port()

    def save_xls(self,auto_result_list,file_path):
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path) # 获取FATP_Marge.csv
        file_name = os.path.splitext(file_name)[0] # 获取FATP_Marge
        save_path = os.path.join(path,file_name+"_result.xls")  
        result_num = 0

        haimeng_xlwt = Haimeng_xlwt(save_path)
        sheet = haimeng_xlwt.xls_book.add_sheet(file_name)
        title = ["command","result","result2"]
        haimeng_xlwt.write_line(sheet,0,0,title,haimeng_xlwt.gray_title_style)
        sheet.col(0).width,sheet.col(1).width,sheet.col(2).width = 10000,20000,20000
        row = 1
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

            sheet.write(row,0,command,haimeng_xlwt.normal_style) # 写入command
            result_column = 1
            while len(str(result))>32760:  #大于这个长度写不进单元格
                if 'WARNING' in result and 'ERROR' not in result and "error" not in result:
                    sheet.write(row,result_column,result[:32760],haimeng_xlwt.yellow_font_style)
                elif 'ERROR' in result or "error" in result:
                    sheet.write(row,result_column,result[:32760],haimeng_xlwt.red_font_style)
                else:
                    sheet.write(row,result_column,result[:32760],haimeng_xlwt.normal_style)
                result = result[32760:]
                result_column += 1
            if len(str(result))>0:
                if 'WARNING' in result and 'ERROR' not in result and "error" not in result:
                    sheet.write(row,result_column,result,haimeng_xlwt.yellow_font_style)
                elif 'ERROR' in result or "error" in result:
                    sheet.write(row,result_column,result,haimeng_xlwt.red_font_style)
                else:
                    sheet.write(row,result_column,result,haimeng_xlwt.normal_style)
            row+=1
        haimeng_xlwt.xls_book.save(save_path)
        self.insert_text_DUT(tk.END,"%d command been read.\n"%(result_num),"green")
        self.insert_text_DUT(tk.END,"result have save at %s\n"%(save_path),"green")

def main(baund_rate):
    dut_sent_command = My_serial(baund_rate, None)

def main_process(baund_rate):
    main_process = Process(target=main, args=(baund_rate,))
    main_process.daemon = True
    main_process.start()

if __name__ == "__main__":
    dut_sent_command = My_serial(115200,None)

        
