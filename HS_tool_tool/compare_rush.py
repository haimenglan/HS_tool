import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage
import os
import re
import platform

class Compare_rush:
    def start_compare(self):
        if platform == "Windows":
            old_sequence = tkfile.askdirectory(title="选择旧版overlay文件夹")
        else:
            old_sequence = tkfile.askdirectory(message="选择旧版overlay文件夹")
        old_version_name = str(old_sequence)
        old_version_name = re.search(r'/.+?$',old_version_name).group()
        for each_file_path in os.walk(old_sequence):
            if "Sequences" in each_file_path[1]:
                old_sequence = each_file_path[0] + "/Sequences"
                print(old_sequence)
                break
        if platform == "Windows":
            new_sequence = tkfile.askdirectory(title="选择新版overlay文件夹")
        else:
            new_sequence = tkfile.askdirectory(message="选择新版overlay文件夹")
        new_version_name = str(new_sequence)
        new_version_name = re.search(r'/.+?$',new_version_name).group()
        for each_file_path in os.walk(new_sequence):
            if "Sequences" in each_file_path[1]:
                new_sequence = each_file_path[0] + "/Sequences"
                print(new_sequence)
                break
        # save_path = '/Users/15400155/Desktop/cmp-rush.txt'
        save_path = tkfile.asksaveasfilename(title = "选择结果保存位置和名称",defaultextension=".txt")
        #不同/新增，删减 
        for each_old_file in os.listdir(old_sequence):
            result = open(save_path,'a')
            if each_old_file in os.listdir(new_sequence) and each_old_file[0]!= '.' and '.rush' in each_old_file:
                old_file_list, new_file_list = [],[]
                old_file_line_index, new_file_line_index = 0,0
                have_change_flag = 0
                change_list = []
                change_list_line_num = 0
                
                #f_old = open(each_old_file,"r")
                #f_new = open(new_sequence+'\\' + os.path.basename(each_old_file))
                f_old = open(old_sequence + '/'+ each_old_file)
                f_new = open(new_sequence +'/'+ each_old_file)
        
                #-------------------获取文件数据------------------
                for each_line in f_old:
                    old_file_list.append(each_line)
                for each_line in f_new:
                    new_file_list.append(each_line)
                #--------------------对比不同-------------------------
                for each_line in new_file_list:
                    new_file_line_index +=1
                    if each_line not in old_file_list:
                        have_change_flag = 1
                        change_list.append("line" + str(new_file_line_index) +':   ' +each_line)
                if have_change_flag:
                    change_list.insert(0,new_version_name+" different with "+old_version_name+": \n")
                    change_list_line_num = len(change_list)
                    
                for each_line in old_file_list:
                    old_file_line_index +=1
                    if each_line not in new_file_list:
                        have_change_flag = 1
                        change_list.append("line" + str(old_file_line_index) +':   ' +each_line)
                if have_change_flag:
                    change_list.insert(change_list_line_num, old_version_name + "\ndifferent with :"+new_version_name+"\n")
                    change_list_line_num = 0
                    change_list.insert(0,' \n\n************************below change from    '+ each_old_file + \
                 ' *******************************************\n\n ')
                    for each_line in change_list:     
                        result.write(each_line)
                    change_list = []
                    have_change_flag = 0
                    
        for each_new_file in os.listdir(new_sequence):
            result = open(save_path,'a')
            if each_new_file not in os.listdir(old_sequence) and each_new_file[0]!= '.' and '.rush' in each_new_file:
                result.write("this is new add rush file:\n" + each_new_file )
    

    
    
    
    
 
