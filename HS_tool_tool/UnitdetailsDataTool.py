#! /usr/bin/env python3
#! /usr/bin/env python
import os
import sys
import time
import re
import csv
from multiprocessing import Process

import xlwt
import xlrd
import platform

from haimeng_xlwt import Haimeng_xlwt

def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while "\\" in path:  
        path = path.replace("\\","")
    return path

class UnitdetailsData:
    def __init__(self, unitdetailsCSV_path, show_empty_mode, is_change_config=False, is_FBR_config=False,
                 FBR_xls_file="", csv_file_path_multi="", **kwargs):
        self.show_empty_mode = show_empty_mode
        self.is_change_config = is_change_config 
        self.is_FBR_config = is_FBR_config
        self.FBR_xls_file = FBR_xls_file
        self.csv_file_path_multi = csv_file_path_multi
        self.is_platinum = False
        if "is_platinum" in kwargs:
            self.is_platinum = kwargs["is_platinum"]
        # 站位排序
        if "order_station_list" in kwargs and kwargs["order_station_list"]:
            self.HealthSensingStation = kwargs["order_station_list"]
        else:
            self.HealthSensingStation = ["TEST8", "DEVELOPMENT22", "TEST1", "DEVELOPMENT15", "TEST5", "TEST24","TEST9",
                                  "SA-BCM", "QT-BCM", 'QT-BCM2', 'DEVELOPMENT2', 'BACK-SENSOR-CAL', 'BACK-SENSOR-TEST',
                                  'STATION230 ', 'DEVELOPMENT3', 'STATION229', 'LEDA', 'DEVELOPMENT1',
                                  'STATION1000','STATION1001','STATION1002','STATION1003','STATION115','STATION108',
                                  'STATION116','STATION110','STATION437','STATION112','STATION358','STATION531',
                                  'STATION435','STATION1238','STATION1227']
        # config 归类
        if self.is_FBR_config and self.is_change_config:
            # xls_file = tkfile.askopenfilename(title="选择LA2x_FRB_QT Dmin_value_table")
            xls_file = self.FBR_xls_file
            #xls_file = change_path(str(input("\033[1;34m choose LA2x_FRB_QT Dmin_value_table: \033[0m")))
            self.change_config_dict = self.read_config_xls(xls_file)
        else:
            self.change_config_dict = {"A":"Aluminum light NDA","B":"Aluminum Dark SP40","C":"SUS Light Polished",
                           "D":"SUS DLC","E":"Evergreen","G":"SUS G1-3","L":"Viper Blue","M":"Viper DLC",
                           "N":"Aluminum Green","P":"Aluminum Rose Gold","R":"Aluminum Red",
                           "U":"Aluminum Blue","S":"Aluminum Stardust","T":"Aluminum Basault",
                           "V":"Viper Nature","Y":"SUS pearl gray"
                           }

        with open(unitdetailsCSV_path) as csvf:  # encoding='utf-8'
            read_csv = csv.reader(csvf)  # read csv file object
            if self.show_empty_mode:
                read_csv = self.show_empty_fail(list(read_csv))
            self.head_line = next(read_csv)
            self.TIME_SPEC = [] # csv的时间区间

            self.STATION_LIST = [] # csv包含的所有站位
            self.ITEM_LIST = {} # csv包含的所有item

            self.STATION_INPUT_DATA = {} # {"TEST5":{total input":0,"fail":0,"retest":0}}
            self.YIELD_DATA = {} # {"TEST5":{"AC_CP:{"num":0,"sn list":[],"station_id list":[],"config list":[]...}}}
            self.RETEST_DATA = {}
            self.STATION_ID_DATA = {} # {"TEST5":{"AC_CP":{ID1:{"retest":0,"fail":0,"sn list":[],"value":[]...}}}}
            self.CONFIG_DATA = {} # {"TEST5":{"AC_CP":{"config1":0,"config2":0...}}
            self.T269_retest_data = {}

            for each_line in read_csv:
                if each_line!=[]:
                    self.init_head(each_line)

                    self.STATION_INPUT_DATA = self.get_station_input_data(self.STATION_INPUT_DATA,each_line)
                    self.YIELD_DATA = self.get_retest_yield_data(self.YIELD_DATA,each_line,"FAIL")
                    self.RETEST_DATA = self.get_retest_yield_data(self.RETEST_DATA,each_line,"RETEST")
                    self.STATION_ID_DATA = self.get_station_id_config_data(self.STATION_ID_DATA,each_line,"station")
                    self.CONFIG_DATA = self.get_station_id_config_data(self.CONFIG_DATA,each_line,"config")
                    self.T269_retest_data = self.get_station_id_config_data(self.T269_retest_data,each_line,"T269")
        self.sort_station_list()

    # 返回新的csv文件
    def show_empty_fail(self, original_csv_line):
        # csv_file_path_multi = tkfile.askopenfilename(title="choose MultitType UnitTestDetails or insight export data which include fail sn")
        csv_file_path_multi = self.csv_file_path_multi
        # 读取 MultitType csv 或 insight export csv
        csv_line_multi = csv_zip.read_csv(csv_file_path_multi)
        for each_line in original_csv_line[:]:  # 读csv文件各个行，按站位筛选 SN,这是因为不同站位可能会出现重复的Sn
            original_csv_sn = each_line[0]
            original_csv_fail_pass = each_line[3]
            original_csv_station_ID = each_line[6]
            original_station_name = original_csv_station_ID.split('_')[-1]
            original_csv_fail_message = each_line[12]
            # 如果当前行的 fail message 为空
            if (original_csv_fail_pass == "FAIL count" or original_csv_fail_pass == "RETEST count") and original_csv_fail_message == "":
                for each_line_muti in csv_line_multi:
                    # ------如果是insight export csv文件 ---------
                    if csv_line_multi[1][0] == "Site":
                        export_csv_item_name = csv_line_multi[1]
                        # 列定位
                        try:
                            # 定义各个 item
                            csv_sn_muti = each_line_muti[export_csv_item_name.index("SerialNumber")]
                            csv_station_ID_muti = each_line_muti[export_csv_item_name.index("Station ID")]
                            csv_fail_pass_muti = each_line_muti[export_csv_item_name.index("Test Pass/Fail Status")]
                            csv_fail_item_muti = each_line_muti[export_csv_item_name.index("List of Failing Tests")]
                            station_name_muti = csv_station_ID_muti.split('_')[-1]
                        except Exception as e:
                            print(e)
                            return original_csv_line
                        else:
                            # 查找数据
                            if original_station_name == station_name_muti and \
                                    csv_sn_muti == original_csv_sn and \
                                    csv_fail_pass_muti == "FAIL" and \
                                    csv_fail_item_muti != "":
                                current_line_index = original_csv_line.index(each_line)
                                original_csv_line[current_line_index][6] = csv_station_ID_muti
                                original_csv_line[current_line_index][9] = csv_fail_item_muti.split(";")[0]
                                break
                    # -------- 如果是 muilti unitdetails 文件 --------
                    else:
                        # 定义各个 item
                        csv_sn_muti = each_line_muti[0]
                        csv_fail_pass_muti = each_line_muti[3]
                        csv_station_ID_muti = each_line_muti[6]
                        csv_fail_item_muti = each_line_muti[9]
                        station_name_muti = csv_station_ID_muti.split('_')[-1]
                        # 查找数据
                        if original_station_name == station_name_muti and \
                                csv_sn_muti == original_csv_sn and \
                                csv_fail_pass_muti == "FAIL" and \
                                csv_fail_item_muti != "":
                            current_line_index = original_csv_line.index(each_line)
                            if original_csv_fail_pass == "FAIL":
                                original_csv_line[current_line_index] = each_line_muti
                            if original_csv_fail_pass == "RETEST":
                                original_csv_line[current_line_index] = each_line_muti
                                original_csv_line[current_line_index][3] = "RETEST"
                            break
        return original_csv_line

    def read_config_xls(self,target_path):
        config_dict = {}
        if target_path!="":
            xls_book = xlrd.open_workbook(target_path)
            for each_table in range(1):
                table = xls_book.sheets()[each_table + 1]
                title_row = table.row_values(0)
                config_col_list, material_col_list = [], []
                if "6C" in title_row:
                    config_col_list = table.col_values(title_row.index("6C"), 1)
                if "Material" in title_row:
                    material_col_list = table.col_values(title_row.index("Material"), 1)
                for key in range(len(config_col_list)):
                    try:
                        config_dict[config_col_list[key]] = material_col_list[key]
                    except Exception as e:
                        print(e)
                        break
        return config_dict

    def init_head(self,each_line):
        self.SN = each_line[0]
        self.PRODUCTION_CODE = each_line[1]
        self.PRODUCT_ASSEMBLY = each_line[2]
        self.TEST_RESULT = each_line[3]
        self.START_TIME = each_line[4]
        self.END_TIME = each_line[5]
        self.STATION_ID = each_line[6]
        self.FIXTURE_ID = each_line[7]
        self.TEST_HEAD = each_line[8]
        self.TEST_ITEM = each_line[9]
        self.SUB_TEST = each_line[10]
        self.SUB_SUB_TEST = each_line[11]
        self.FAIL_MESSAGE = each_line[12]
        self.MEASUREMENT_VALUE = each_line[13]
        self.LOWER_LIMIT = each_line[14]
        self.UPPER_LIMIT = each_line[15]
        self.UNIT = each_line[16]
        self.PARENT_SPECIAL_BUILD_NAME = each_line[17]
        self.CHILD_SPECIAL_BUILD_NAME = each_line[18]
        self.CONFIGURATION_CODE = each_line[19]

        self.STATION_NAME = self.get_station_name(each_line) 
        if self.STATION_NAME not in self.STATION_LIST:
            self.STATION_LIST.append(self.STATION_NAME)
        if self.STATION_NAME not in self.ITEM_LIST:
            self.ITEM_LIST[self.STATION_NAME] = []
        if self.TEST_ITEM not in self.ITEM_LIST[self.STATION_NAME] and(self.TEST_RESULT=="FAIL" or self.TEST_RESULT=="RETEST" ):
            self.ITEM_LIST[self.STATION_NAME].append(self.TEST_ITEM)
        self.STATION_ID_SLOT = self.get_station_id(each_line)
        self.CONFIG = self.get_config(each_line)
        self.T269_CONFIG = self.get_T269_config(self.CHILD_SPECIAL_BUILD_NAME)

        if self.TIME_SPEC == []:
            self.TIME_SPEC = [self.START_TIME,self.START_TIME]
        else:
            self.TIME_SPEC = self.get_time_spec(self.START_TIME,self.TIME_SPEC)

    def search_time(self,time):
        time_search_re = re.search(r"(\d{4}).(\d{1,2}).(\d{1,2}).{1,2}(\d{1,2}):(\d{1,2})",time)
        year,month,day,hour,minute = time_search_re.group(1),time_search_re.group(2),time_search_re.group(3),\
                                        time_search_re.group(4),time_search_re.group(5)
        return [year,month,day,hour,minute]

    def compare_time(self,time1,time2):
        try:
            time1_list = self.search_time(time1)
            time2_list = self.search_time(time2)
            i=0
            for each_time in time1_list:
                if int(each_time) > int(time2_list[i]):
                    return True
                elif int(each_time) < int(time2_list[i]):
                    return False
                i+=1
            return False # time1=time2
        except Exception as e:
            # default return None
            print("compare time failed",time1,time2)

    def get_time_spec(self,time,time_spec):
        is_small = self.compare_time(time,time_spec[0])
        is_large = self.compare_time(time,time_spec[1])
        if is_small is not None:
            if not is_small:
                time_spec[0] = time
        if is_large is not None:
            if is_large:
                time_spec[1] = time
        return time_spec

    def get_station_name(self,each_line):
        if '_' in self.STATION_ID:
            station_name = self.STATION_ID.split('_')[-1]
        else:
            station_name = self.STATION_ID
        return station_name

    # change staitonID name
    def get_station_id(self,each_line):
        if (self.TEST_HEAD != '') and ('TEST8' not in self.STATION_ID) \
                and ('TEST5' not in self.STATION_ID) \
                and ("DEVELOPMENT15" not in self.STATION_ID):
            if len(self.TEST_HEAD) > 4:
                if self.TEST_HEAD == "1234":
                    new_station_id = self.STATION_ID + '_slot_' + self.TEST_HEAD
                elif "TEST24" in self.STATION_ID:
                    new_station_id = self.STATION_ID + '_slot_' + self.TEST_HEAD[-1]
                else:
                    new_station_id = self.STATION_ID + '_slot_' + self.TEST_HEAD[1]
            else:
                new_station_id = self.STATION_ID + '_slot_' + self.TEST_HEAD
            return new_station_id
        else:
            return self.STATION_ID

    def sort_station_list(self):
        station_index = 0
        for each_station in self.HealthSensingStation:  # 排序站位
            if each_station in self.STATION_LIST:  # 如果healthsensing中的站位在csv里面，就按顺序排列self.station
                self.STATION_LIST.remove(each_station)
                self.STATION_LIST.insert(station_index, each_station)
                station_index += 1

    def change_config(self,config):
        if self.is_FBR_config:
            if config in self.change_config_dict:
                return self.change_config_dict[config]
            else:
                return  config
        else:
            if "_" in config:
                new_config = config.split('_')[-1][0]
                if new_config in self.change_config_dict:
                    new_config = self.change_config_dict[new_config]
                    return new_config
                else:
                    return config
            else:
                return config
            
    def get_config(self,each_line):
        if self.is_FBR_config:
            config = self.CONFIGURATION_CODE 
        else:
            config = self.CHILD_SPECIAL_BUILD_NAME
        if self.is_change_config:
            config = self.change_config(config)
        return config

    def get_T269_config(self,child_special_build):
        new_code = re.search(r"L\w+\d\w",child_special_build)
        config_dict = {"N187B":"LA2B","N187S":"LA2A","N188B":"LA2D","N187S":"LA2C"}
        if new_code!=None:
            return new_code.group()
        elif self.PRODUCTION_CODE in config_dict:
            return config_dict[self.PRODUCTION_CODE]
        else:
            return child_special_build

    # Performance Breakdown 
    def get_station_input_data(self,station_input_data,each_line):
        if self.STATION_NAME not in station_input_data:
            station_input_data[self.STATION_NAME] = {}
            station_input_data[self.STATION_NAME]["total input"] = 0
            station_input_data[self.STATION_NAME]["total fail"] = 0
            station_input_data[self.STATION_NAME]["total retest"] = 0
            station_input_data[self.STATION_NAME]["station"] = {}
            station_input_data[self.STATION_NAME]["config"] = {}
            station_input_data[self.STATION_NAME]["T269"] = {}

        if self.STATION_ID_SLOT not in station_input_data[self.STATION_NAME]["station"]:
            station_input_data[self.STATION_NAME]["station"][self.STATION_ID_SLOT] = 0
        if self.CONFIG not in station_input_data[self.STATION_NAME]["config"]:
            station_input_data[self.STATION_NAME]["config"][self.CONFIG] = 0
        if self.T269_CONFIG not in station_input_data[self.STATION_NAME]["T269"]:
            station_input_data[self.STATION_NAME]["T269"][self.T269_CONFIG] = 0

        station_input_data[self.STATION_NAME]["total input"] += 1
        station_input_data[self.STATION_NAME]["station"][self.STATION_ID_SLOT] += 1
        station_input_data[self.STATION_NAME]["config"][self.CONFIG] += 1
        station_input_data[self.STATION_NAME]["T269"][self.T269_CONFIG] += 1

        if self.TEST_RESULT=="FAIL":
            station_input_data[self.STATION_NAME]["total fail"]+=1
        if self.TEST_RESULT=="RETEST":
            station_input_data[self.STATION_NAME]["total retest"]+=1
        return station_input_data

    def get_fail_message(self,test_item,sub,sub_sub,fail_message):
        all_fail_message = ""
        if test_item != "":
            all_fail_message += test_item
        if sub != "":
            all_fail_message += "_"+sub
        if sub_sub != "":
            all_fail_message += "_"+sub_sub
        if fail_message != "":
            all_fail_message += " "+fail_message
        return all_fail_message

    def get_retest_yield_data(self,retest_yield_data,each_line,retest_fail):
        if self.STATION_NAME not in retest_yield_data:
            retest_yield_data[self.STATION_NAME] = {}
        if self.TEST_RESULT==retest_fail:
            if self.TEST_ITEM not in retest_yield_data[self.STATION_NAME]:
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM] = {}
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["num"] = 0
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["value"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["fail message"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["sn"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["station"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["config"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["child_special_build"] = []
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["start time"] = []

                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["upper limit"] = self.UPPER_LIMIT
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["lower limit"] = self.LOWER_LIMIT
                retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["unit"] = self.UNIT
            
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["num"] += 1
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["value"].append(self.MEASUREMENT_VALUE)
            all_fail_message = self.get_fail_message(self.TEST_ITEM,self.SUB_TEST,self.SUB_SUB_TEST,self.FAIL_MESSAGE)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["fail message"].append(all_fail_message)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["sn"].append(self.SN)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["station"].append(self.STATION_ID_SLOT)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["config"].append(self.CONFIG)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["child_special_build"].append(self.CHILD_SPECIAL_BUILD_NAME)
            retest_yield_data[self.STATION_NAME][self.TEST_ITEM]["start time"].append(self.START_TIME)
        
        return retest_yield_data

    def get_station_id_config_data(self,station_id_config_data,each_line,station_config):
        if station_config == "station":
            key = self.STATION_ID_SLOT
        elif station_config == "config":
            key = self.CONFIG
        elif station_config == "T269":
            key = self.T269_CONFIG

        if self.STATION_NAME not in station_id_config_data:
            station_id_config_data[self.STATION_NAME] = {}
        if self.TEST_RESULT=="FAIL" or self.TEST_RESULT=="RETEST":
            if self.TEST_ITEM not in station_id_config_data[self.STATION_NAME]: 
            # {"TEST5":{"AC_CP":{ID1:{"retest":0,"fail":0,"sn list":[],"value":[]...}}}}
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM]={}
            if key not in station_id_config_data[self.STATION_NAME][self.TEST_ITEM]:
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM][key] = {}
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM][key]["retest"] = 0
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM][key]["fail"] = 0

            if self.TEST_RESULT=="FAIL" :
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM][key]["fail"] += 1
            elif self.TEST_RESULT=="RETEST" :
                station_id_config_data[self.STATION_NAME][self.TEST_ITEM][key]["retest"] += 1
        return station_id_config_data



class Unitdetails_xls(Haimeng_xlwt):
    def __init__(self, xls_path, unitdetailsData):
        super().__init__(xls_path)
        self.unitdetailsData = unitdetailsData
        self.yield_summary,self.retest_summary = {},{}
        self.T269_item = {"all_station":["Dut"],"LEDA":["Dut","UART"]}

        self.write_Performance_Breakdown()
        is_platinum = unitdetailsData.is_platinum
        print("is platinum", is_platinum)
        self.write_Yield(is_platinum)
        self.write_retest(is_platinum)
        self.write_summary()
        self.write_station_id_config("station")
        self.write_station_id_config("config")
        self.write_line_breakdown()
        T269_row,T269_sheet = self.write_T269_LAxABCD()
        self.write_T269_Dock(T269_row+1,T269_sheet)
        self.write_T269_SN()
        self.xls_book.save(xls_path)
        if platform.system()=="Darwin":
            print("文件保存在",xls_path)
            os.system(f"open {xls_path}")

    def write_Performance_Breakdown(self):
        title = ["Station Type","Yield","Input","Fail Count","Fail %","Pass Count","Retest Count","Retest %"]
        sheet = self.xls_book.add_sheet("Performance_Breakdown")
        sheet.col(0).width = 10000
        self.write_line(sheet,1,0,title,self.gray_title_style)
        row = 2
        summary = "Summary:\n"+str(self.unitdetailsData.TIME_SPEC[0])+" ~ "+str(self.unitdetailsData.TIME_SPEC[1])+"\nRTR\n"
        for each_station in self.unitdetailsData.STATION_LIST:
            total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total input"]
            fail = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total fail"]
            pass_ = total - fail
            retest = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total retest"]
            yield_ = f"{pass_/total:.2%}"
            fail_rate = f"{fail/total:.2%}"
            #retest_rate = "%.2f"%(100*(retest/total))+"%"
            retest_rate = f"{retest/total:.2%}"
            summary += str(each_station)+" input: "+str(total)+"x, RTR: "+retest_rate+"\n"
            column = 0
            sheet.write(row,column,each_station,self.station_style)
            column+=1
            line = [str(yield_),total,fail,str(fail_rate),pass_,retest,str(retest_rate)]
            self.write_line(sheet,row,column,line,self.normal_style,persent_column = [1,4,7])
            row+=1
        sheet.write(0,0,summary,self.normal_style)
        #self.set_blank(sheet,0,row,0,len(title))

    def get_station_id_num(self,station_id_list):
        all_station_id = ""
        station_id_dict = {} # {"id1":{"num":3,"slot1":1}}
        for each_station in station_id_list:
            if "_slot_" in each_station:
                station_id = each_station.split("_slot_")[0]
            else:
                station_id = each_station
            if station_id not in station_id_dict:
                station_id_dict[station_id] = {}
                station_id_dict[station_id]["num"] = 0
            station_id_dict[station_id]["num"] += 1

            if "slot_" in each_station:
                slot = each_station.split("_slot_")[1]
                if "slot_"+slot not in station_id_dict[station_id]:
                    station_id_dict[station_id]["slot_"+slot] = 0
                station_id_dict[station_id]["slot_"+slot] += 1

        for each_station in station_id_dict:
            all_station_id += str(station_id_dict[each_station]["num"])+"x "+each_station
            if len(station_id_dict[each_station])>1:
                all_station_id += ":\n"
                for each_slot in station_id_dict[each_station]:
                    if each_slot!="num":
                        all_station_id += "    " +str(station_id_dict[each_station][each_slot])+"x "+each_slot+"\n"
            else:
                all_station_id += "\n"
        return all_station_id

    def get_config_num(self,config_list):
        config_dict = {}
        all_config_num = ""
        for each_config in config_list:
            if each_config not in config_dict:
                config_dict[each_config] = 0
            config_dict[each_config] += 1
        for each_config in config_dict:
            all_config_num += str(config_dict[each_config])+"x "+each_config+"\n"
        return all_config_num

    def get_fa_result(self,fail_message_list,value_list,upper_limit,lower_limit,unit):
        fa_result = ""
        for each_fail in fail_message_list:
            if each_fail not in fa_result:
                fa_result += each_fail +"\n"
        if re.search(r"\d",str(value_list)) is not None:
            fa_result += "test value: "
            for each_value in value_list:
                fa_result += str(each_value)+", "
        if upper_limit!="" or lower_limit!="":
            fa_result += "limit: ["+lower_limit+","+upper_limit+"]"
        return fa_result

    def get_remark(self,sn_list,station_id_list,config_list,time_list):
        remark = ""
        for i in range(len(sn_list)):
            remark+=sn_list[i]+" ("+station_id_list[i]+",  "+config_list[i]+",  "+time_list[i]+")\n"
        return remark

    def get_retest_yield_data(self,total,station_retest_yield_data):
        fail = station_retest_yield_data["num"]
        fail_rate = "%.2f"%(100*(fail/total))+"%"
        fail_sn = ""
        for each_sn in station_retest_yield_data["sn"]:
            fail_sn += each_sn+"\n"
        all_station_id = self.get_station_id_num(station_retest_yield_data["station"])
        all_config_num = self.get_config_num(station_retest_yield_data["config"])
        fa_result = self.get_fa_result(station_retest_yield_data["fail message"],
                                        station_retest_yield_data["value"],
                                        station_retest_yield_data["upper limit"],
                                        station_retest_yield_data["lower limit"],
                                        station_retest_yield_data["unit"]
                                      )
        remark = self.get_remark(station_retest_yield_data["sn"],
                                 station_retest_yield_data["station"],
                                 station_retest_yield_data["config"],
                                 station_retest_yield_data["start time"])
        return fail,fail_rate,fail_sn,all_station_id,all_config_num,fa_result,remark

    # 按某一列排序列表
    def sort_insert_line(self,all_line,line,sort_column):
        if all_line==[]:
            all_line.append(line)
        else:
            insert_index = 0
            for each_line in all_line:
                if line[sort_column]>each_line[sort_column]: # fail/retest num
                    all_line.insert(insert_index,line)
                    return all_line
                insert_index+=1
            if insert_index==len(all_line): # no one in all line smaller than line
                all_line.append(line)
        return all_line

    def get_yield_retest_summary(self,all_line,qty_index,item_index,fa_index):
        summary = ""
        for each_line in all_line:
            if "NA" in each_line[item_index]:
                summary += "NA"
            else:
                summary += str(each_line[qty_index])+"x "+each_line[item_index]+"\n"+ \
                        "RC: "+each_line[fa_index]+"\n"+ \
                        "CA: \n\n"
        return summary

    def write_Yield(self, is_platinum=False):
        title = ["Station","Input","Pass","Fail Count","Fail Rate","Fail Item","Failure SN","FA Result","Station ID","config","Remark"]
        sheet = self.xls_book.add_sheet("Yield")
        self.write_line(sheet,1,0,title,self.gray_title_style)  
        row = 2

        width = {0:6000,5:9000,6:7000,7:12000,8:9000,9:9000,10:22000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            all_line = []
            total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total input"]
            pass_ = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total input"] - \
                        self.unitdetailsData.STATION_INPUT_DATA[each_station]["total fail"]
            if self.unitdetailsData.YIELD_DATA[each_station]!={}:
                for each_item in self.unitdetailsData.YIELD_DATA[each_station]:
                    fail,fail_rate,fail_sn,all_station_id,all_config_num,fa_result,remark =\
                         self.get_retest_yield_data(total,self.unitdetailsData.YIELD_DATA[each_station][each_item])
                    line = ["", total, pass_, fail, fail_rate, each_item, fail_sn, fa_result, all_station_id,
                            all_config_num, remark]
                    all_line = self.sort_insert_line(all_line, line, 3)
                all_line[0][0] = each_station
                # +++++++++++++ 适配platinum 格式 ++++++++++++
                if is_platinum:
                    new_all_line = []
                    for i, each_line in enumerate(all_line):
                        if i==0:
                            new_all_line = each_line[:]
                            new_all_line[5] = f"{each_line[3]}x {each_line[5]}"
                            new_all_line[7] = f"{each_line[3]}x {each_line[5]}:\nRC: {each_line[7]}\n\n"
                            for i in range(8,11):
                                new_all_line[i] = f"{each_line[3]}x {each_line[5]}:\n{each_line[i]}\n"
                        else:
                            new_all_line[3] += each_line[3]
                            new_all_line[4] = f"{new_all_line[3]/new_all_line[1]:.2%}"
                            new_all_line[5] +=f"\n{each_line[3]}x {each_line[5]}"
                            new_all_line[6] += f"{each_line[6]}"
                            new_all_line[7] += f"{each_line[3]}x {each_line[5]}:\nRC: {each_line[7]}\n\n"
                            for i in range(8, 11):
                                new_all_line[i] += f"{each_line[3]}x {each_line[5]}:\n{each_line[i]}\n"
                    all_line = [new_all_line]
            else:
                all_line = [[each_station,total,total,0,"0%","NA","NA","NA","NA","NA","NA"]]
            for each_line in all_line:
                self.write_line(sheet,row,0,each_line,self.normal_style)       
                row+=1
            if each_station not in self.yield_summary:
                self.yield_summary[each_station] = ""
            if not is_platinum:
                self.yield_summary[each_station] += self.get_yield_retest_summary(all_line,qty_index=3,item_index=5,fa_index=7)
            else:
                self.yield_summary[each_station] += all_line[0][5]
        #self.set_blank(sheet,1,row,0,len(title))

    def write_retest(self, is_platinum=False):
        title = ["station","Input","Retest Qty","Retest Rate","Retest Item","Failure SN","Station ID","Root Cause",
                    "Corrective Action","config","remark"]
        sheet = self.xls_book.add_sheet("Retest")
        self.write_line(sheet,1,0,title,self.gray_title_style)    
        row = 2

        width = {0:6000,4:9000,5:7000,6:9000,7:12000,8:12000,9:9000,10:22000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            all_line = []
            total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total input"]
            if self.unitdetailsData.RETEST_DATA[each_station]!={}:
                for each_item in self.unitdetailsData.RETEST_DATA[each_station]:
                    retest,retest_rate,retest_sn,all_station_id,all_config_num,fa_result,remark = \
                         self.get_retest_yield_data(total,self.unitdetailsData.RETEST_DATA[each_station][each_item])
                    line = ["",total,retest,retest_rate,each_item,retest_sn,all_station_id,fa_result,"",all_config_num,remark]
                    # sort by retest num
                    all_line = self.sort_insert_line(all_line,line,3)
                # +++++++++++++ 适配platinum 格式 ++++++++++++
                if is_platinum:
                    new_all_line = []
                    for i, each_line in enumerate(all_line):
                        station_list = self.unitdetailsData.RETEST_DATA[each_station][each_line[4]]['station']
                        if i == 0:
                            new_all_line = each_line[:]
                            new_all_line[4] = f"\n{each_line[2]}x {each_line[4]}"  # item
                            new_all_line[6] = ""  # station
                            for each_stationID in station_list:
                                # if each_stationID not in new_all_line[6]:
                                new_all_line[6] += f"{each_stationID}\n"
                            new_all_line[7] = f"{each_line[2]}x {each_line[4]}:\nRC: {each_line[7]}\n\n"
                            new_all_line[8] = f"{each_line[2]}x {each_line[4]}:\n{each_line[6]}\n\n"
                            for i in range(9, 11):
                                new_all_line[i] = f"{each_line[2]}x {each_line[4]}:\n{each_line[i]}\n"
                        else:
                            new_all_line[2] += each_line[2]  # retest
                            new_all_line[3] = f"{new_all_line[2] / new_all_line[1]:.2%}"  # retest rate
                            new_all_line[4] += f"\n{each_line[2]}x {each_line[4]}"  # item
                            new_all_line[5] += f"{each_line[5]}"  # sn
                            for each_stationID in station_list:
                                # if each_stationID not in new_all_line[6]:
                                new_all_line[6] += f"{each_stationID}\n"  # station
                            new_all_line[7] += f"{each_line[2]}x {each_line[4]}:\nRC: {each_line[7]}\n\n"
                            new_all_line[8] += f"{each_line[2]}x {each_line[4]}:\n{each_line[6]}\n\n"
                            for i in range(9, 11):
                                new_all_line[i] += f"{each_line[2]}x {each_line[4]}:\n{each_line[i]}\n"
                    all_line = [new_all_line]
            else:
                all_line = [[each_station,total,0,"0%","NA","NA","NA","NA","NA","NA","NA"]]
            all_line[0][0] = each_station
            for each_line in all_line:       
                self.write_line(sheet,row,0,each_line,self.normal_style)  
                row+=1
            if each_station not in self.retest_summary:
                self.retest_summary[each_station] = ""
            if not is_platinum:
                self.retest_summary[each_station] += self.get_yield_retest_summary(all_line,2,4,7)
            else:
                self.retest_summary[each_station] += all_line[0][4]
        #self.set_blank(sheet,1,row,0,len(title))

    def write_summary(self):
        title = ["station","Input","Pass","FR","Fail item/Root Cause(TOP 3)","RR","Retest item/action(TOP 3)"]
        sheet = self.xls_book.add_sheet("Summary")
        self.write_line(sheet,1,0,title,self.gray_title_style)    
        row = 2

        width = {0:6000,4:15000,6:15000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total input"]
            fail = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total fail"]
            pass_ = total - fail
            retest = self.unitdetailsData.STATION_INPUT_DATA[each_station]["total retest"]
            yield_ = "%.2f"%(100*(pass_/total))+"%"
            fail_rate = "%.2f"%(100*(fail/total))+"%"
            retest_rate = "%.2f"%(100*(retest/total))+"%"
            line = [each_station,total,pass_,fail_rate,self.yield_summary[each_station],retest_rate,self.retest_summary[each_station]]
            self.write_line(sheet,row,0,line,self.normal_style)  
            row+=1
        #self.set_blank(sheet,1,row,0,len(title))

    def write_station_id_config(self,key_type):
        title = ["Station","Item",key_type,"Input","Retest count","Retest rate","Fail count","Fail rate"]
        sheet = self.xls_book.add_sheet(key_type)
        self.write_line(sheet,1,0,title,self.gray_title_style)    
        row = 2

        width = {0:6000,1:9000,2:14000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        if key_type=="station":
            station_id_config_data = self.unitdetailsData.STATION_ID_DATA
        elif key_type=="config":
            station_id_config_data = self.unitdetailsData.CONFIG_DATA
        for each_station in self.unitdetailsData.STATION_LIST:
            for each_item in self.unitdetailsData.ITEM_LIST[each_station]:
                #for each_id in self.unitdetailsData.STATION_ID_DATA[each_station][each_item]:
                all_line = []
                for each_id in self.unitdetailsData.STATION_INPUT_DATA[each_station][key_type]:
                    total = self.unitdetailsData.STATION_INPUT_DATA[each_station][key_type][each_id]
                    if each_id in station_id_config_data[each_station][each_item]:
                        retest = station_id_config_data[each_station][each_item][each_id]["retest"]
                        fail = station_id_config_data[each_station][each_item][each_id]["fail"]
                    else:
                        retest,fail = 0,0
                    if total!=0:
                        retest_rate = "%.2f"%(100*(retest/total))+"%"
                        fail_rate = "%.2f"%(100*(fail/total))+"%"
                    else:
                        retest_rate,fail_rate = "NA"
                    line = ["","",each_id,total,retest,retest_rate,fail,fail_rate]
                    all_line = self.sort_insert_line(all_line,line,4)
                all_line[0][0],all_line[0][1] = each_station,each_item
                for each_line in all_line:
                    self.write_line(sheet,row,0,each_line,self.normal_style)  
                    row+=1
        #self.set_blank(sheet,1,row,0,len(title))

    def sort_station_insert_line(self,all_line,line,station_id_index):
        if all_line==[]:
            all_line.append(line)
            return all_line
        insert_index = 0
        for each_line in all_line:
            search_each_line_re = re.search(r"(\d+)_(\d+).*?(\d)*$",each_line[station_id_index])
            search_line_re = re.search(r"(\d+)_(\d+).*?(\d)*$",line[station_id_index])
            if search_each_line_re is not None and search_line_re is not None:
                if int(search_each_line_re.group(1))>int(search_line_re.group(1)):  # compare LG/SM line
                    all_line.insert(insert_index,line)
                    return all_line
                elif int(search_each_line_re.group(1))==int(search_line_re.group(1)): 
                    if int(search_each_line_re.group(2))>int(search_line_re.group(2)):  # compare station id 
                        all_line.insert(insert_index,line)
                        return all_line
                    elif int(search_each_line_re.group(2))==int(search_line_re.group(2)): # compare slot
                        if search_each_line_re.group(3) is not None:
                            if search_line_re.group(3) is not None:
                                if int(search_each_line_re.group(3))>int(search_line_re.group(3)):
                                    all_line.insert(insert_index,line)
                                    return all_line
                                else:
                                    insert_index+=1
                                    continue
                    else:
                        insert_index+=1
                        continue
                else:
                    insert_index+=1
                    continue
        if insert_index == len(all_line):
            all_line.append(line)
        return all_line

    def calculate_line_FR_RR(self,all_line):
        first_line = re.search(r"(.*)_\d*_",all_line[0][1]).group(1)
        target_line_retest,target_line_fail,target_line_total = 0,0,0
        station_retest,station_fail,station_total = 0,0,0

        line_index = 0
        for each_line in all_line:
            current_line = re.search(r"(.*)_\d*_",each_line[1]).group(1)
            current_line_retest = int(each_line[5].split("R/")[0])
            current_line_fail = int(each_line[2].split("F/")[0])
            current_line_total = int(re.search(r"(\d+)T",each_line[2]).group(1))
            if current_line != first_line:
                all_line[line_index-1][3]= str(target_line_fail)+"F/"+str(target_line_total)+"T="+ \
                                            "%.2f"%(100*(target_line_fail/target_line_total))+"%"
                all_line[line_index-1][6]= str(target_line_retest)+"R/"+str(target_line_total)+"T="+ \
                                            "%.2f"%(100*(target_line_retest/target_line_total))+"%"
                first_line = current_line
                target_line_retest,target_line_fail,target_line_total = current_line_retest,current_line_fail,current_line_total
                station_retest += current_line_retest
                station_fail += current_line_fail
                station_total += current_line_total
                line_index+=1
                continue
            target_line_retest += current_line_retest
            target_line_fail += current_line_fail
            target_line_total += current_line_total
            station_retest += current_line_retest
            station_fail += current_line_fail
            station_total += current_line_total
            line_index+=1
        all_line[line_index-1][3]= str(target_line_fail)+"F/"+str(target_line_total)+"T="+ \
                                            "%.2f"%(100*(target_line_fail/target_line_total))+"%"
        all_line[line_index-1][6]= str(target_line_retest)+"R/"+str(target_line_total)+"T="+ \
                                    "%.2f"%(100*(target_line_retest/target_line_total))+"%"
        all_line[line_index-1][4]= str(station_fail)+"F/"+str(station_total)+"T="+ \
                                            "%.2f"%(100*(station_fail/station_total))+"%"
        all_line[line_index-1][7]= str(station_retest)+"R/"+str(station_total)+"T="+ \
                                    "%.2f"%(100*(station_retest/station_total))+"%"
        return all_line


    def write_line_breakdown(self):
        title = ["Station","station_ID","FR","FR_line","FR_total","RR","RR_line","RR_total"]
        sheet = self.xls_book.add_sheet("Line Break Down")
        self.write_line(sheet,1,0,title,self.gray_title_style)    
        row = 2

        width = {0:6000,1:12000,2:6000,3:6000,4:6000,5:6000,6:6000,7:6000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            all_line = []
            # calculate station id retest and fail
            for each_id in self.unitdetailsData.STATION_INPUT_DATA[each_station]["station"]:
                current_id_total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["station"][each_id]
                current_id_retest,current_id_fail = 0,0
                for each_item in self.unitdetailsData.STATION_ID_DATA[each_station]:
                    if each_id in self.unitdetailsData.STATION_ID_DATA[each_station][each_item]:
                        current_id_retest += self.unitdetailsData.STATION_ID_DATA[each_station][each_item][each_id]["retest"]
                        current_id_fail += self.unitdetailsData.STATION_ID_DATA[each_station][each_item][each_id]["fail"]
                FR = str(current_id_fail)+"F/"+str(current_id_total)+"T="+"%.2f"%(100*(current_id_fail/current_id_total))+"%"
                RR = str(current_id_retest)+"R/"+str(current_id_total)+"T="+"%.2f"%(100*(current_id_retest/current_id_total))+"%"
                line = ["",each_id,FR,"","",RR,"",""]
                all_line = self.sort_station_insert_line(all_line,line,1)
            # calculate line retest and fail
            all_line = self.calculate_line_FR_RR(all_line)
            if all_line!=[]:
                all_line[0][0] = each_station
            for each_line in all_line:
                self.write_line(sheet,row,0,each_line,self.normal_style)
                row+=1
        #self.set_blank(sheet,1,row,0,len(title))

    def get_T269_LAxABCD_title(self):
        title = []
        for each_station in self.unitdetailsData.STATION_LIST:
            for each_LA in self.unitdetailsData.STATION_INPUT_DATA[each_station]["T269"]:
                if each_LA not in title:
                    title.append(each_LA)
        title = sorted(title)
        all_title = []
        for each_title in title:
            all_title.append(each_title+"_input")
            all_title.append(each_title+"_Retest")
            all_title.append(each_title+"_RR")
        return title,all_title

    def write_T269_LAxABCD(self):
        title,all_title = self.get_T269_LAxABCD_title()
        sheet = self.xls_book.add_sheet("T269_LAxABCD")
        self.write_line(sheet,1,0,["station"]+["LAx_ABCD_input","LAxABCD_retest_count","LAxABCD_RR"]+all_title,self.gray_title_style)    
        row = 2

        width = {0:6000,2:12000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            line = []
            all_LA_total,all_LA_retest,all_LA_fail = 0,0,0
            for each_LA in title:
                if each_LA in self.unitdetailsData.STATION_INPUT_DATA[each_station]["T269"]:
                    total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["T269"][each_LA]
                else:
                    total = 0
                all_LA_total += total
                retest,fail = 0,0
                if each_station in self.T269_item:
                    T269_item_list = self.T269_item[each_station]
                else:
                    T269_item_list = self.T269_item["all_station"]
                for each_item in T269_item_list:
                    if each_item in self.unitdetailsData.T269_retest_data[each_station]:
                        if each_LA in self.unitdetailsData.T269_retest_data[each_station][each_item]:
                            retest += self.unitdetailsData.T269_retest_data[each_station][each_item][each_LA]["retest"]
                            fail += self.unitdetailsData.T269_retest_data[each_station][each_item][each_LA]["fail"]
                            all_LA_retest += retest
                            all_LA_fail += fail
                if total!=0:
                    retest_rate = "%.2f"%(100*(retest/total))+"%"
                    fail_rate = "%.2f"%(100*(fail/total))+"%"
                else:
                    retest_rate,fail_rate = "NA","NA"
                line += [total,retest,retest_rate]
            if all_LA_total!=0:
                all_LA_retest_rate = "%.2f"%(100*(all_LA_retest/all_LA_total))+"%"
                all_LA_fail_rate = "%.2f"%(100*(all_LA_fail/all_LA_total))+"%"
            else:
                all_LA_retest_rate,all_LA_fail_rate = "NA","NA"
            line = [all_LA_total,all_LA_retest,all_LA_retest_rate] + line
            self.write_line(sheet,row,0,[each_station]+line,self.normal_style)  
            row+=1
        return row,sheet

    def get_line_size(self,each_id):
        size = ""
        search_line = re.search(r"(\d+)_(\d+).*?(\d)*$",each_id)
        if search_line is not None:
            if search_line.group(1)=="01":
                return "SM"
            elif search_line.group(1)=="02":
                return "LG"
        return size
        
    def write_T269_Dock(self,row,sheet):
        title = ["Station","line","Station ID","Retest Count","Retest Rate"]
        self.write_line(sheet,row,0,title,self.gray_title_style)    
        row += 1
        for each_station in self.unitdetailsData.STATION_LIST:
            all_line = []
            # calculate station id retest and fail
            for each_id in self.unitdetailsData.STATION_INPUT_DATA[each_station]["station"]:
                current_id_total = self.unitdetailsData.STATION_INPUT_DATA[each_station]["station"][each_id]
                current_id_retest,current_id_fail = 0,0
                if each_station in self.T269_item:
                    T269_item_list = self.T269_item[each_station]
                else:
                    T269_item_list = self.T269_item["all_station"]
                for each_item in T269_item_list:
                    if each_item in self.unitdetailsData.STATION_ID_DATA[each_station]:
                        if each_id in self.unitdetailsData.STATION_ID_DATA[each_station][each_item]:
                            current_id_retest += self.unitdetailsData.STATION_ID_DATA[each_station][each_item][each_id]["retest"]
                            current_id_fail += self.unitdetailsData.STATION_ID_DATA[each_station][each_item][each_id]["fail"]
                FR = str(current_id_fail)+"F/"+str(current_id_total)+"T="+"%.2f"%(100*(current_id_fail/current_id_total))+"%"
                retest_count = str(current_id_retest)+"R/"+str(current_id_total)+"T"
                RR = "%.2f"%(100*(current_id_retest/current_id_total))+"%"
                size = self.get_line_size(each_id)
                line = ["",size,each_id,retest_count,RR]
                all_line = self.sort_station_insert_line(all_line,line,2)
            if all_line!=[]:
                all_line[0][0]=each_station
            for each_line in all_line:
                self.write_line(sheet,row,0,each_line,self.normal_style)
                row+=1

    def write_T269_SN(self):
        title = ["Station","Product Type","Config","DUT SN","Dock SN","Fail Message (T269)"]
        sheet = self.xls_book.add_sheet("T269_SN")
        self.write_line(sheet,1,0,title,self.gray_title_style)    
        row = 2

        width = {2:11000,3:9000,4:9000,5:15000}  
        for each_column in width:
            sheet.col(each_column).width = width[each_column]

        for each_station in self.unitdetailsData.STATION_LIST:
            if each_station in self.T269_item:
                T269_item_list = self.T269_item[each_station]
            else:
                T269_item_list = self.T269_item["all_station"]
            for each_item in T269_item_list:
                if each_item in self.unitdetailsData.RETEST_DATA[each_station]:
                    i = 0
                    for each_sn in self.unitdetailsData.RETEST_DATA[each_station][each_item]["sn"]:
                        config = self.unitdetailsData.RETEST_DATA[each_station][each_item]["child_special_build"][i]
                        product_type = self.unitdetailsData.get_T269_config(config)
                        fa_result = self.unitdetailsData.RETEST_DATA[each_station][each_item]["fail message"][i]
                        station_id = self.unitdetailsData.RETEST_DATA[each_station][each_item]["station"][i]
                        line = [each_station,product_type,config,each_sn,station_id,fa_result]
                        self.write_line(sheet,row,0,line,self.normal_style)
                        row+=1
        #self.set_blank(sheet,1,row,0,len(title))

def main(csv_path, xls_save_path, show_empty_mode = False, is_change_config = False, is_FBR_config = False,
         FBR_xls_file="",csv_file_path_multi="", is_platinum=False, order_station_list=None):
    if csv_path != "":
        # print(show_empty_mode,is_change_config,is_FBR_config)
        unitdetailsData = UnitdetailsData(csv_path, show_empty_mode, is_change_config,
                                          is_FBR_config,FBR_xls_file,csv_file_path_multi, is_platinum=is_platinum, order_station_list=None)
        if xls_save_path != "":
            unitdetails_xls = Unitdetails_xls(xls_save_path, unitdetailsData)
            print("\033[1;34mResult file have saved at \033[1;32m %s\033[0m" % (xls_save_path))

def run_daily_report(csv_path, xls_save_path, show_empty_mode = False,is_change_config = False,is_FBR_config = False,
                     FBR_xls_file="",csv_file_path_multi="", is_platinum=False, order_station_list=None):
    run_daily_report_process = Process(target=main,args=(csv_path,xls_save_path,show_empty_mode,is_change_config,is_FBR_config,
                                                         FBR_xls_file,csv_file_path_multi,is_platinum, order_station_list, ))
    run_daily_report_process.daemon = True
    run_daily_report_process.start()


if __name__ == "__main__":
    pass
    # 终端运行如下
    # csv_path = change_path(str(input("\033[1;34m input unitdetails csv file: \033[0m")))
    # is_change_config=False
    # is_FBR_config=False
    # unitdetailsData = UnitdetailsData(csv_path,is_change_config,is_FBR_config)
    # save_name = input("\033[1;34m input save name: \033[0m")
    # xls_path = os.path.join(os.path.dirname(csv_path),save_name+".xls")
    # unitdetails_xls = Unitdetails_xls(xls_path,unitdetailsData)
    # print("\033[1;34mResult file have saved at \033[1;32m %s\033[0m"%(xls_path))




