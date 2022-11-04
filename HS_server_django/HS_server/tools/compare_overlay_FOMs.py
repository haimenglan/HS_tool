#! /usr/bin/env python3
#! /usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import zipfile
import os
import sys
import time
import xlwt
import xlrd


class Csv_zip:
   def __init__(self):
      pass

   def read_csv(self,file_path):
      csv_line = []
      try:
         with open(file_path,encoding='utf-8') as csvf:
            read_csv = csv.reader(csvf)  # 读csv文件
            for each_line in read_csv:  # 读csv文件各个行
               if each_line != []:
                  csv_line.append(each_line)
            return csv_line
      except Exception as e:
         print("read csv error, please save csv file as 'utf-8' file and re-try",str(e))

   def write_csv(self,file_path,value_list):
      f= open(file_path, 'w', encoding='utf-8')
      csv_writer = csv.writer(f)
      for each_line in value_list:
         csv_writer.writerow(each_line)
      f.close()

   def zip(self):
      pass

   def unzip(self,file_path,target_path):
      if not os.path.exists(target_path):
         os.makedirs(target_path)
      zip_file_f = zipfile.ZipFile(file_path,"r",zipfile.ZIP_DEFLATED)
      extract_file_list = zip_file_f.namelist() # 获取压缩文件中的文件列表
      if len(extract_file_list):
         for each_file in extract_file_list:
            zip_file_f.extract(each_file,target_path)


class Insight_csv:
   insight_csv_num = 0
   def __init__(self,csv_file_path):
      Insight_csv.insight_csv_num+=1
      self.csv_zip = Csv_zip()
      if csv_file_path!="":
         self.csv_line = self.csv_zip.read_csv(csv_file_path)
         self.init_csv_index()
         self.csv_value = self.get_csv_value()

   def init_csv_index(self):
      self.fom_line = self.csv_line[1]
      self.upper_limit_line = self.csv_line[4]
      self.lower_limit_line = self.csv_line[5]
      self.unit_line = self.csv_line[6]
      self.data_start_row = 7
      try:
         self.overlay_version = self.csv_line[7][self.fom_line.index("Version")]
         self.overlay_station = self.csv_line[7][self.fom_line.index("Station ID")]
         if '_' in self.overlay_station:
            self.overlay_station = self.overlay_station.split('_')[-1]
      except Exception as e:
         self.overlay_version = "file_"+str(Insight_csv.insight_csv_num)
         self.overlay_station = f'station_{Insight_csv.insight_csv_num}'
         print("can't find overlay version in csv file")
      try:
         self.fom_start_column = self.csv_line[0].index("Parametric")
      except Exception as e:
         #self.fom_start_column = filter(lambda item: item if item!="" else None,self.lower_limit_line[1:])
         self.fom_start_column = self.lower_limit_line.index(list(filter(None, self.lower_limit_line[1:]))[0])

   def get_csv_value(self):
      value = {}
      for each_line in self.csv_line[self.data_start_row:]:
         item_index = 0
         for each_item in self.fom_line:
            if each_item not in value:
               value[each_item] = []
            value[each_item].append(each_line[item_index])
            item_index += 1
      return value

class Overlay_compare_fom:
   def __init__(self,por_csv_path,new_csv_path):
      self.por_csv = Insight_csv(por_csv_path)
      self.new_csv = Insight_csv(new_csv_path)
      self.miss_foms,self.new_add_foms,self.same_foms,self.same_foms_limit_change = self.get_compare_fom_data()

   def get_compare_fom_data(self):
      miss_foms = [] # [{fom:"xxx", "limit":"xxx", "unit":"xxx"},...]
      new_add_foms = [] # [{fom:"xxx", "limit":"xxx", "unit":"xxx"},...]
      same_foms = [] # [{fom:"xxx", "limit":"xxx", "unit":"xxx"},...]
      same_foms_limit_change = [] # [{"fome":"xxx", "por limit":"xxx", "por unit":"xxx", "new limit":"xxx", "new unit":"xxx"},...]

      por_index,new_index = self.por_csv.fom_start_column,self.new_csv.fom_start_column
      for each_por_fom in self.por_csv.fom_line[self.por_csv.fom_start_column:]:
         if each_por_fom not in self.new_csv.fom_line: # misss fom
            this_limit = "["+self.por_csv.lower_limit_line[por_index]+","+self.por_csv.upper_limit_line[por_index]+"]"
            this_fom = {"fom":each_por_fom,"limit":this_limit,"unit":self.por_csv.unit_line[por_index]}
            miss_foms.append(this_fom)
         por_index+=1
      for each_new_fom in self.new_csv.fom_line[self.new_csv.fom_start_column:]:
         if each_new_fom not in self.por_csv.fom_line: # new add fom
            this_limit = "["+self.new_csv.lower_limit_line[new_index]+","+self.new_csv.upper_limit_line[new_index]+"]"
            this_fom = {"fom":each_new_fom,"limit":this_limit,"unit":self.new_csv.unit_line[new_index]}
            new_add_foms.append(this_fom)
         new_index+=1

      por_index = self.por_csv.fom_start_column
      for each_por_fom in self.por_csv.fom_line[self.por_csv.fom_start_column:]:
         new_index = self.new_csv.fom_start_column
         for each_new_fom in self.new_csv.fom_line[self.new_csv.fom_start_column:]:
            if each_por_fom==each_new_fom: # find same fom
               # same fom but limit change
               if self.por_csv.upper_limit_line[por_index] == self.new_csv.upper_limit_line[new_index] and \
                  self.por_csv.lower_limit_line[por_index] == self.new_csv.lower_limit_line[new_index]: # find same fom
                  this_limit = "["+self.por_csv.lower_limit_line[por_index]+","+self.por_csv.upper_limit_line[por_index]+"]"
                  this_fom = {"fom":each_por_fom,"limit":this_limit,"unit":self.por_csv.unit_line[por_index]}
                  same_foms.append(this_fom)
               # same fom but limit change
               else:
                  por_limit = "["+self.por_csv.lower_limit_line[por_index]+","+self.por_csv.upper_limit_line[por_index]+"]"
                  new_limit = "["+self.new_csv.lower_limit_line[new_index]+","+self.new_csv.upper_limit_line[new_index]+"]"
                  por_unit = self.por_csv.unit_line[por_index]
                  new_unit = self.new_csv.unit_line[new_index]
                  this_fom = {"fom":each_por_fom,"por limit":por_limit,"por unit":por_unit,
                           "new limit":new_limit,"new unit":new_unit}
                  same_foms_limit_change.append(this_fom)

            new_index+=1
         por_index+=1
      return miss_foms,new_add_foms,same_foms,same_foms_limit_change


class Html_table:
   def __init__(self):
      '''
      一个表格
      '''
      self.table_content = ""

   def write_header(self, header):
      self.table_content += "<tr>"
      for i in header:
         self.table_content += f"<th>{i}</th>"
      self.table_content += "</tr>"

   def write_line(self, line, style=None):
      '''
      向表格写入一行， style是一个字典，key是对应line的索引，value是样式
      '''
      self.table_content += "<tr>"
      for i, item in enumerate(line):
         if style is not None:
            if i in style:
               self.table_content += f"<td style={style[i]}>{item}</td>"
            elif "all" in style:
               self.table_content += f"<td style={style['all']}>{item}</td>"
            else:
               self.table_content += f"<td>{item}</td>"
         else:
            self.table_content += f"<td>{item}</td>"
      self.table_content += "</tr>"

   @property
   def table(self):
      return f"<table border=1 cellspacing=0 style='font-size:12px;'>{self.table_content}</table>"


class Html_xls:
   def __init__(self):
      '''
      相当于一个xls文件，self.xls字典，key保存的是xls文件中每个sheet名字，value保存每个sheet包含的表格
      '''
      self.xls = {}
      self.sheet_name_list = []  # 用来排序sheet

   def add_table_to_sheet(self, sheet_name, table_name, table, table_name_style='margin-top:30px;',
                          table_style='margin-bottom:30px;'):
      if sheet_name not in self.xls:
         self.sheet_name_list.append(sheet_name)
         self.xls[sheet_name] = f"<div class='sheet'></div>"
      # 添加表格标题
      self.xls[sheet_name] = self.xls[sheet_name][:-6] + f"<div style='{table_name_style}'>{table_name}</div>"
      # 添加表格内容
      self.xls[sheet_name] += f"<div style='{table_style}'>{table}</div>" + "</div>"

   # def finish_add_sheet(self, sheet_name):
   #    self.xls[sheet_name] = f"<div class='sheet'>{self.xls[sheet_name]}</div>"


class My_xlwt:
   def __init__(self,file_path):
      self.xls_file_path = file_path
      self.save_path = ""
      self.xls_book = xlwt.Workbook()
      self.html_xls = Html_xls()
      self.html_table = Html_table()


   def set_style(self,font_name, font_height, font_colour=1, font_bold=False,pattern_colour=1 ):
      style = xlwt.XFStyle()  # 新建风格
      font = xlwt.Font()  # 新建字体
      font.name = font_name
      font.bold = font_bold  # 是否加粗
      font.colour_index = font_colour
      font.height = font_height

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
      style.alignment.wrap = 1
      return style

   def init_compare_fom_style(self):
      self.normal_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=1)
      self.name_style = self.set_style('Helvetisca', 250, font_colour=0, font_bold=True,pattern_colour=1)
      self.title_style = self.set_style('Helvetica', 250, font_colour=0, font_bold=True, pattern_colour=22)
      self.miss_foms_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,pattern_colour=5)
      self.new_add_foms_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=7)
      self.same_foms_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False, pattern_colour=3)
      self.same_foms_limit_change_style = self.set_style('Helvetica', 220, font_colour=0, font_bold=False,
                                             pattern_colour=52)

   def read_config_xls(self):
      xls_book = xlrd.open_workbook(self.xls_file_path)
      config_dict = {}
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

   def write_compare_fom_title(self,sheet,por_version,new_version):
      self.html_table.write_line(["Remove FOMs"], {0: "background-color:rgb(253,250,65)"})
      self.html_table.write_line(["New Add FOMs"], {0: "background-color:rgb(97,252,250)"})
      self.html_table.write_line(["Same FOMs but limit change"], {0: "background-color:rgb(238,134,48)"})
      self.html_table.write_line(["Same FOMs"], {0: "background-color:rgb(102,247,50)"})
      self.html_table.write_line(["POR: "], {0: "font-weight:bold"})
      self.html_table.write_line(["NEW: "], {0: "font-weight:bold"})

      sheet.write(0, 0, "Remove FOMs", self.miss_foms_style)
      #sheet.write(0, 1, "Miss FOMs", self.name_style)
      sheet.write(1, 0, "New Add FOMs", self.new_add_foms_style)
      #sheet.write(1, 1, "New Add FOMs", self.name_style)
      sheet.write(2, 0, "Same FOMs but limit change", self.same_foms_limit_change_style)
      #sheet.write(2, 1, "Same FOMs but change limit", self.name_style)
      sheet.write(3, 0, "Same FOMs", self.same_foms_style)
      #sheet.write(3, 1, "Same FOMs", self.name_style)
      sheet.write(4,0,"POR: "+por_version,self.name_style)
      #sheet.write(4,1,"POR: ",self.name_style)
      sheet.write(5,0,"NEW: "+new_version,self.name_style)
      #sheet.write(5,1,"NEW: ",self.name_style)

   def write_miss_fom(self,sheet,row,each_fom):
      line = [each_fom["fom"], "", each_fom["limit"], "", each_fom["unit"], ""]
      self.html_table.write_line(line, {0: "background-color:rgb(253,250,65)",
                                        2: "background-color:rgb(253,250,65)", 4: "background-color:rgb(253,250,65)"})
      sheet.write(row, 0, each_fom["fom"],self.miss_foms_style)
      sheet.write(row, 2, each_fom["limit"], self.miss_foms_style)
      sheet.write(row, 4, each_fom["unit"], self.miss_foms_style)


   def write_new_add_fom(self,sheet,row,each_fom):
      line = ["", each_fom["fom"], "", each_fom["limit"], "", each_fom["unit"]]
      self.html_table.write_line(line, {1: "background-color:rgb(97,252,250)",
                                        3: "background-color:rgb(97,252,250)", 5: "background-color:rgb(97,252,250)"})
      sheet.write(row,1,each_fom["fom"],self.new_add_foms_style)
      sheet.write(row, 3, each_fom["limit"], self.new_add_foms_style)
      sheet.write(row, 5, each_fom["unit"], self.new_add_foms_style)

   def write_same_fom(self,sheet,row,each_fom):
      line = [each_fom["fom"], each_fom["fom"], each_fom["limit"], each_fom["limit"], each_fom["unit"], each_fom["unit"]]
      self.html_table.write_line(line, {"all": "background-color:rgb(102,247,50)"})
      sheet.write(row,0,each_fom["fom"],self.same_foms_style)
      sheet.write(row, 1, each_fom["fom"], self.same_foms_style)
      sheet.write(row, 2, each_fom["limit"], self.same_foms_style)
      sheet.write(row, 3, each_fom["limit"], self.same_foms_style)
      sheet.write(row, 4, each_fom["unit"], self.same_foms_style)
      sheet.write(row, 5, each_fom["unit"], self.same_foms_style)

   def write_same_fom_but_limit_change(self,sheet,row,each_fom):
      line = [each_fom["fom"], each_fom["fom"], each_fom["por limit"], each_fom["new limit"], each_fom["por unit"],
              each_fom["new unit"]]
      self.html_table.write_line(line, {"all": "background-color:rgb(238,134,48)"})
      sheet.write(row,0,each_fom["fom"],self.same_foms_limit_change_style)
      sheet.write(row,1, each_fom["fom"], self.same_foms_limit_change_style)
      sheet.write(row, 2, each_fom["por limit"], self.same_foms_limit_change_style)
      sheet.write(row, 3, each_fom["new limit"], self.same_foms_limit_change_style)
      sheet.write(row, 4, each_fom["por unit"], self.same_foms_limit_change_style)
      sheet.write(row, 5, each_fom["new unit"], self.same_foms_limit_change_style)

   def write_compare_fom_result(self,compare_fom_obj):
      por_version = str(compare_fom_obj.por_csv.overlay_version)
      new_version = str(compare_fom_obj.new_csv.overlay_version)
      sheet = self.xls_book.add_sheet("FOMs")
      self.init_compare_fom_style()
      self.write_compare_fom_title(sheet,por_version,new_version)

      title_list = ["POR_FOMs","NEW_FOMs","POR_Limit","NEW_Limit","POR_Unit","NEW_Unit"]
      self.html_table.write_line(title_list, style={"all":"background-color:gray; font-weight:bold;"})
      for each_title in range(len(title_list)):
         sheet.write(6,each_title,title_list[each_title],self.title_style)
      sheet.col(0).width,sheet.col(1).width,sheet.col(2).width,sheet.col(3).width,sheet.col(4).width,sheet.col(5).width\
         = 15000,15000,3200,3200,3000,3000
      row = 7
      for each_fom in compare_fom_obj.miss_foms:
         self.write_miss_fom(sheet,row,each_fom)
         row+=1
      for each_fom in compare_fom_obj.new_add_foms:
         self.write_new_add_fom(sheet,row,each_fom)
         row+=1
      for each_fom in compare_fom_obj.same_foms_limit_change:
         self.write_same_fom_but_limit_change(sheet,row,each_fom)
         row+=1
      for each_fom in compare_fom_obj.same_foms:
         self.write_same_fom(sheet,row,each_fom)
         row+=1
      self.html_xls.add_table_to_sheet("sheet", "compare_FOMs_result", self.html_table.table)

   def get_max_min_mean(self,value_list):
      max_value,min_value,mean_value = "","",""
      if value_list!=[]:
         for each_value in value_list:
            if each_value!="":
               max_value,min_value,mean_value=float(each_value),float(each_value),[]
               break
         for each_value in value_list:
            if each_value!="":
               if float(each_value)>max_value:
                  max_value = float(each_value)
               if float(each_value)<min_value:
                  min_value = float(each_value)
               mean_value.append(float(each_value))
         if len(mean_value) == 0:
            mean_value = ""
         else:
            mean_value = sum(mean_value) / len(mean_value)
      return max_value,min_value,mean_value

   def get_spec(self,fom_line,lower_limit_line,upper_limit_line,each_fom):
      fom_index = fom_line.index(each_fom)
      upper_limit = upper_limit_line[fom_index]
      lower_limit = lower_limit_line[fom_index]
      if upper_limit=="NA":
         upper_limit = 0
      if lower_limit=="NA":
         lower_limit = 0
      spec = float(upper_limit) - float(lower_limit)
      return spec

   def get_max_sub_min_persent(self,max_value,min_value,spec):
      if max_value != "":
         max_sub_min = max_value - min_value
      else:
         max_sub_min = ""

      if spec != 0.0 and max_sub_min != "":
         xx_persent = max_sub_min / spec
      elif max_sub_min == "":
         xx_persent = ""
      else:
         xx_persent = "NA"
      return max_sub_min,xx_persent


   def write_compare_data(self,row,sheet,data_kind,each_fom,compare_fom_obj):
      this_line = []
      por_max, por_min, por_mean, por_max_sub_min, por_persent = "", "", "", "", ""
      new_max, new_min, new_mean, new_max_sub_min, new_persent = "", "", "", "", ""
      mean_persent = ""
      if data_kind=="miss" or "same" in data_kind :
         por_max,por_min,por_mean = self.get_max_min_mean(compare_fom_obj.por_csv.csv_value[each_fom])
         por_spec = self.get_spec(compare_fom_obj.por_csv.fom_line,compare_fom_obj.por_csv.lower_limit_line,
                                  compare_fom_obj.por_csv.upper_limit_line,each_fom)
         por_max_sub_min,por_persent = self.get_max_sub_min_persent(por_max,por_min,por_spec)

      if data_kind=="new_add" or "same" in data_kind :
         new_max,new_min,new_mean = self.get_max_min_mean(compare_fom_obj.new_csv.csv_value[each_fom])
         new_spec = self.get_spec(compare_fom_obj.new_csv.fom_line,compare_fom_obj.new_csv.lower_limit_line,
                                  compare_fom_obj.new_csv.upper_limit_line,each_fom)
         new_max_sub_min,new_persent = self.get_max_sub_min_persent(new_max,new_min,new_spec)

      if por_mean!=0 and por_mean!="" and new_mean!="":
         mean_persent = (por_mean-new_mean)/por_mean
      elif por_mean=="" and new_mean=="":
         mean_persent = ""
      else:
         mean_persent = "NA"

      this_line = [each_fom,por_max,new_max,por_min,new_min,por_max_sub_min,new_max_sub_min,
                     por_persent,new_persent,por_mean,new_mean,mean_persent]

      for each_data in range(len(this_line)):
         if (each_data == 7 or each_data == 8 or each_data == 11) and "str" not in str(type(this_line[each_data])):
            if this_line[each_data]>0.03 or this_line[each_data]<-0.03:
               sheet.write(row,each_data,"%.2f"%(100*this_line[each_data])+"%",self.miss_foms_style)
            else:
               sheet.write(row,each_data,"%.2f"%(100*this_line[each_data])+"%",self.normal_style)
         elif each_data == 0:
            if data_kind=="miss":
               sheet.write(row,each_data,this_line[each_data],self.miss_foms_style)
            elif data_kind=="new_add":
               sheet.write(row,each_data,this_line[each_data],self.new_add_foms_style)
            elif data_kind=="same":
               sheet.write(row,each_data,this_line[each_data],self.same_foms_style)
            elif data_kind=="same but limit change":
               sheet.write(row,each_data,this_line[each_data],self.same_foms_limit_change_style)
         else:
            sheet.write(row,each_data,this_line[each_data],self.normal_style)


      
   def write_compare_data_result(self,compare_fom_obj):
      sheet = self.xls_book.add_sheet("Test value")
      por_version = str(compare_fom_obj.por_csv.overlay_version)
      new_version = str(compare_fom_obj.new_csv.overlay_version)
      por_station_name = str(compare_fom_obj.por_csv.overlay_station)
      new_station_name = str(compare_fom_obj.new_csv.overlay_station)
      self.write_compare_fom_title(sheet,por_version,new_version)
      title = ["FOM",
               "POR_Max","NEW_Max",
               "POR_Min","NEW_Min",
               "POR(Max-Min)","NEW(Max-Min)",
               "POR(Max-Min)/Spec","NEW(Max-Min)/Spec",
               "POR_Mean","NEW_Mean",
               "(POR-NEW)/POR_Mean"
      ]

      for each_title in range(len(title)):
         sheet.write(6,each_title,title[each_title],self.title_style)
      sheet.col(0).width = 15000
      for each_title in range(len(title)):
         sheet.col(each_title+1).width = 3000

      row=7
      for each_fom in compare_fom_obj.miss_foms:
         self.write_compare_data(row,sheet,"miss",each_fom["fom"],compare_fom_obj)
         row+=1
      # print("new add++++++", compare_fom_obj.new_add_foms)
      for each_fom in compare_fom_obj.new_add_foms:
         self.write_compare_data(row,sheet,"new_add",each_fom["fom"],compare_fom_obj)
         row+=1
      for each_fom in compare_fom_obj.same_foms_limit_change:
         self.write_compare_data(row,sheet,"same but limit change",each_fom["fom"],compare_fom_obj)
         row+=1
      # print("same++++++", compare_fom_obj.same_foms)
      for each_fom in compare_fom_obj.same_foms:
         self.write_compare_data(row,sheet,"same",each_fom["fom"],compare_fom_obj)
         row+=1

      if por_station_name == new_station_name:
         self.save_path = self.xls_file_path+"/"+ por_station_name+"_"+por_version+"_VS_"+new_version+".xls"
      else:
         self.save_path = self.xls_file_path+"/"+ por_station_name+"_"+por_version+"_VS_"+ new_station_name+"_"+new_version+".xls"

      self.xls_book.save(self.save_path)
      print("\033[1;34mResult file have saved at \033[1;32m %s\033[0m"%(self.save_path))

      # self.html_xls.add_table_to_sheet("compare_FOMs_result", "compare FOMs result", self.html_table.table)

def change_path(path):
    while " " == path[-1]:
        path = path[:-1]
    while "\\" in path:  
        path = path.replace("\\","")
    return path

def main(por_path, new_path, save_path):
   overlay_compare_fom = Overlay_compare_fom(por_path, new_path)
   my_xlwt = My_xlwt(save_path)
   my_xlwt.write_compare_fom_result(overlay_compare_fom)
   my_xlwt.write_compare_data_result(overlay_compare_fom)
   return my_xlwt

if __name__ == "__main__":
   por_path = change_path(str(input("\033[1;34m input POR version insight export csv file path:\033[0m")))
   new_path = change_path(str(input("\033[1;34m input NEW version insight export csv file path:\033[0m")))
   save_path = os.path.dirname(new_path)
   main(por_path, new_path, save_path)


   
