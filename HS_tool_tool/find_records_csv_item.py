#! /usr/bin/env python3
#! /usr/bin/env python
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfile

import tkinter.messagebox as tkmessage
import os
import sys
import time

import xlwt
import csv
import re

from haimeng_xlwt import Haimeng_xlwt

def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while "\\" in path:  
        path = path.replace("\\","")
    return path

#————————————————————————————————搜索全部records.csv 中的测试项——————————————————————————————       
class Rcords_csv:
    def __init__(self,file_path,search_mode,row_column_mode,find_name):
        #self.data_directory = change_path(input(title = 'choose data path'))
        self.data_directory = file_path
        self.records_csv_file_list = []
        self.find_name_list = find_name
        # Atlas1 列索引
        self.name1 = 0
        self.name2 = 1
        self.name3 = 2
        self.name4 = 3
        self.measure_value = 6
        self.upper_limit = 8
        self.lower_limit = 9
        self.unit = 7
        self.pass_fail = 4
        self.fail_message = 5
        # atlas2 索引
        # self.name1 = 1 
        # self.name2 = 2
        # self.name3 = 3
        # self.name4 = 4
        # self.measure_value = 7
        # self.upper_limit = 6
        # self.lower_limit = 8
        # self.unit = 10
        # self.pass_fail = 12
        # self.fail_message = 13

        # 模式
        self.search_mode = search_mode
        self.row_column_mode = row_column_mode
        self.excel_value_list = []
        self.insight_csv_list = []
        self.init_title()

    # 获取所有文件路径
    def get_all_file(self):
        file_num = 0
        for each_file_list in os.walk(self.data_directory):
            if "Records.csv" in each_file_list[2] or "records.csv" in each_file_list[2]:
                file_num += 1 #20210310_15-56-55
                #file_time 
                self.records_csv_file_list.append(each_file_list[0]+'/'+"Records.csv")
        print('文件数量是',str(file_num))
        self.records_csv_file_list.sort()
        #self.records_csv_file_list = sorted(self.records_csv_file_list)
        return self.records_csv_file_list

    # 读取csv各个行
    def read_csv(self,file_path):
        csv_line = []
        i = 0
        with open(file_path,encoding='utf-8') as csvf:
            read_csv = csv.reader(csvf)
            for each_line in read_csv:
                if each_line != []:
                    csv_line.append(each_line)
        return csv_line

    def init_title(self):
        self.insight_csv_list.append(["xx_station_data", '', '', '', '', '', '', '', '', '', '', '', 'Parametric'])
        self.insight_csv_list.append(
            ["Site", "Product", "SerialNumber", "Special Build Name", "Special Build Description",
             "Unit Number", "Station ID", "Test Pass/Fail Status", "StartTime", "EndTime",
             "Version", "List of Failing Tests"])

        self.insight_csv_list.append(["Display Name ----->", '', '', '', '', '', '', '', '', '', '', ''])
        self.insight_csv_list.append(["PDCA Priority ----->", '', '', '', '', '', '', '', '', '', '', ''])
        self.insight_csv_list.append(["Upper Limit ----->", '', '', '', '', '', '', '', '', '', '', ''])
        self.insight_csv_list.append(["Lower Limit ----->", '', '', '', '', '', '', '', '', '', '', ''])
        self.insight_csv_list.append(["Measurement Unit ----->", '', '', '', '', '', '', '', '', '', '', ''])

        sheet_title = ['name1', 'neme2', 'name3', 'name4', 'upper_limit', 'lower_limit', 'unit']
        self.excel_value_list.append(sheet_title)

    def get_excel_value_list(self,each_line,title_list,add_file_num):
        sheet_title = [each_line[self.name1],
                       each_line[self.name2],
                       each_line[self.name3],
                       each_line[self.name4],
                       each_line[self.upper_limit],
                       each_line[self.lower_limit],
                       each_line[self.unit]
                       ]
        if sheet_title not in title_list:  # 此项为新增，前面已添加的文件没有这个测项都要添加值为空
            title_list.append(sheet_title[:])
            self.excel_value_list.append(sheet_title[:])
            for each_file in range(add_file_num-1):
                self.excel_value_list[-1].append('')  # 新增测项的前面测试的每个SN/文件值为空
        mesurement_value = each_line[self.measure_value]  #后面没有查找到的测项也要设为空值
        item_index = title_list.index(sheet_title)
        self.excel_value_list[item_index+1].append(mesurement_value)
        return title_list

    def get_insight_value_list(self,insight_csv_list_line,each_line,insight_title_list,add_file_num,pass_fail,fail_message):
        new_pass_fail = pass_fail
        item_name = each_line[self.name2]
        if each_line[self.name3] != "":
            item_name += "_" + each_line[self.name3]
        if each_line[self.name4] != "":
            item_name += "_" + each_line[self.name4]
        if item_name not in insight_title_list:
            insight_csv_list_line.append("")
            insight_title_list.append(item_name[:])
            self.insight_csv_list[1].append(item_name)

            if each_line[self.upper_limit]=="":
                each_line[self.upper_limit]="NA"
            if each_line[self.lower_limit]=="":
                each_line[self.lower_limit] = "NA"
            if each_line[self.unit]=="":
                each_line[self.unit] = "NA"

            self.insight_csv_list[4].append(each_line[self.upper_limit])
            self.insight_csv_list[5].append(each_line[self.lower_limit])
            self.insight_csv_list[6].append(each_line[self.unit])
            for each_file in range(add_file_num-1):
                self.insight_csv_list[each_file+7].append('') # 此项为新增，前面已添加的文件没有这个测项都要添加值为空

        mesurement_value = each_line[self.measure_value]
        # if measure_value =="":
        #     measure_value = "NA"
        item_index = insight_title_list.index(item_name)
        insight_csv_list_line[item_index+12] = mesurement_value #在对应测项的位置写入测试值
        if each_line[self.pass_fail] == "FAIL":
            new_pass_fail = "FAIL"
            fail_message += each_line[self.name2] + ":" + each_line[self.fail_message] + ";  "
        return insight_title_list,insight_csv_list_line,new_pass_fail,fail_message

    def get_sn_station(self,each_file):
        path_list = each_file.split("/")
        time = path_list[-3]
        sn = path_list[-4]
        station = path_list[-5]
        insight_csv_list_line = ['', '', sn, '', '', '', station, '', time, '', '', '']
        return insight_csv_list_line

    def search_item(self):
        self.records_csv_file_list = self.get_all_file()
        add_file_num = 0
        title_list = []
        insight_title_list = []
        for each_file in self.records_csv_file_list:  # 读取每个文件
            add_file_num += 1
            read_file = self.read_csv(each_file)
            # 表格
            self.excel_value_list[0].append(each_file)
            # insight_csv
            pass_fail = "PASS"
            fail_message = ''
            insight_csv_list_line = self.get_sn_station(each_file)
            line_num = 0
            for each_name in range(len(insight_title_list)):
                insight_csv_list_line.append("")  # 先按测项名把列表补齐
            for each_line in read_file: # 读取文件的每一行
                is_add_line = False
                line_num += 1
                if self.search_mode == 0:  # 查找全部数据
                    if each_line[self.measure_value] != '': # 只要测试值不为空，这一行就要
                        is_add_line = True
                else:
                    for each_name in self.find_name_list:
                        if each_name in each_line: # 只要这一行包含我要查找的名字，这一行我就要
                            is_add_line = True
                            break
                if is_add_line:
                    title_list = self.get_excel_value_list(each_line,title_list,add_file_num)
                    if line_num!=1:
                        insight_title_list,insight_csv_list_line,pass_fail,fail_message = \
                            self.get_insight_value_list(insight_csv_list_line,each_line,insight_title_list,add_file_num,pass_fail,fail_message)
            insight_title_list.append("0")
            for each_name in range(len(title_list)):
                if len(self.excel_value_list[each_name+1])-7 < add_file_num:
                    self.excel_value_list[each_name+1].append("")  # 没查找到的测项，值设置为空
            insight_csv_list_line[7] = pass_fail
            insight_csv_list_line[11] = fail_message
            insight_csv_list_line.append("0")
            self.insight_csv_list.append(insight_csv_list_line)
        return self.excel_value_list

    def write_insihgt_csv(self,file_path,value_list):
        f= open(file_path+"_insight.csv", 'w', encoding='utf-8')
        csv_writer = csv.writer(f)
        for each_line in value_list:
            csv_writer.writerow(each_line)

    def write_item_to_xls(self,value_list,style):
        f = xlwt.Workbook()
        sheet_num = 1

        if self.row_column_mode:
            row = len(value_list)
            column = len(value_list[0])  #缺少排序
        else:
            column = len(value_list)
            row = len(value_list[0])
        if column>255:
            sheet_num = column//255 + 1

        for each_num in range(sheet_num):
            sheet = f.add_sheet('sheet_'+str(each_num))
            start_column = each_num*255
            if (each_num+1)*255 <column:
                end_column = (each_num+1)*255
            else:
                end_column = column
            for i in range(row):
                for j in range(start_column,end_column):
                    if self.row_column_mode:
                        try:
                            sheet.write(i, j-start_column, value_list[i][j], style)
                        except Exception as e:
                            pass
                            #print('写入表格报错',e)
                    else:
                        try:
                            sheet.write(i, j-start_column, value_list[j][i], style)
                        except Exception as e2:
                            pass
                            #print('写入表格报错',e2)

        save_file_path = tkfile.asksaveasfilename(title = "选择保存位置和名称",defaultextension=".xls")                                                 
        f.save(save_file_path[:-4]+"_excel.xls")
        self.write_insihgt_csv(save_file_path[:-4],self.insight_csv_list)


if __name__ == "__main__":
    file_path = change_path(input(title = 'choose data path'))
    search_mode = 0
    row_column_mode = False
    records_csv = Rcords_csv(file_path,search_mode, row_column_mode, [])
    haimeng_xlwt = Haimeng_xlwt()
    style = haimeng_xlwt.normal_style
    sheet_value_list = records_csv.search_item()
    records_csv.write_item_to_xls(sheet_value_list, style)



