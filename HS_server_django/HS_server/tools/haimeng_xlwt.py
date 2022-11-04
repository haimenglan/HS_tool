import os,sys,time
import xlwt
import xlrd

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






