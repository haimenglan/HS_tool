import time
import pymysql


class HS_mysql:
    def __init__(self):
        self.hs_mysql = pymysql.connect(host='127.0.0.1', port=3306, database='HealthSensingTool',
                                        user='root', password='lm141747', charset='utf8')
        self.hs_mysql_cursor = self.hs_mysql.cursor()

    # 普通查询
    def search(self, table_name, field_list, condition, params=None):
        command = "select "
        for i, each_field in enumerate(field_list):
            if i==len(field_list)-1:
                command += f"{each_field} from {table_name} {condition};"
            else:
                command += f"{each_field},"
        # print("查询数据命令是", command, params)
        if params is not None:
            # 防止sql注入，command="select account from Contact where account = %s", params=["haimeng_lan"]
            result_count = self.hs_mysql_cursor.execute(command, params)
        else:
            result_count = self.hs_mysql_cursor.execute(command)
        result = self.hs_mysql_cursor.fetchall()
        # print("查询数据结果是", result)
        # 如果没有数据返回单元组()，如果有数据返回双元组((),)
        return result

    def make_field_for_inner_join(self, table, field_list):
        command = ""
        for i, each_field in enumerate(field_list):
            if i==len(field_list)-1:
                command += f"{table}.{each_field} "
            else:
                command += f"{table}.{each_field},"
        return command

    # 连接查询
    def inner_join_search(self, table1, field_list1, table2, field_list2, condition, params=None):
        """
        command = select c.account,c.photo, c.sign, r.nickname from contact as c inner join relationship as r on
              r.friend_account in ("Chao_Jiang", "Haimeng_Lan") and c.account=r.friend_account and 
              r.owner_account="Haimeng_Lan" and c.is_online=b'1' order by r.time desc limit 0,100;
        command = select Contact.account, Contact.photo, Contact.sign, Contact.is_online, relationship.nickname from Contact 
                    inner join relationship on Contact.account=relationship.account and relationship_account='Haimeng_Lan' and...
        """
        command = "select "
        command += self.make_field_for_inner_join(table1, field_list1)+","
        command += self.make_field_for_inner_join(table2, field_list2)
        command += f"from {table1} inner join {table2} {condition};"
        # print("查询数据命令是", command)
        if params is not None:
            result_count = self.hs_mysql_cursor.execute(command, params)
        else:
            result_count = self.hs_mysql_cursor.execute(command)
        result = self.hs_mysql_cursor.fetchall()
        # print("查询数据结果是", result)
        return result

    # 修改
    def modify(self, table, field_dict, condition, params=None ):
        # update Contact set fd=11, cookie='xxx-xxx',is_online=b"1" where account="Haimeng_Lan";
        command = f"update {table} set "
        for i,key in enumerate(field_dict):
            if "str" in str(type(field_dict[key])):
                command+=f"{key}='{field_dict[key]}'"
            else:
                command+=f"{key}={field_dict[key]}"
            if i==len(field_dict)-1:
                command+=f" {condition};"
            else:
                command+=","
        # print("修改指令是", command)
        try:
            if params:
                result_count = self.hs_mysql_cursor.execute(command, params)
            else:
                result_count = self.hs_mysql_cursor.execute(command)
            self.hs_mysql.commit()
            # print("修改成功")
            return True
        except Exception as e:
            # print("修改失败", e)
            return False

    def delete(self, table, condition, params):
        command = f"delete from {table} {condition}"
        # print("删除指令是",command,params)
        try:
            if params:
                result_count = self.hs_mysql_cursor.execute(command, params)
            else:
                result_count = self.hs_mysql_cursor.execute(command)
            self.hs_mysql.commit()
            # print("删除成功")
        except Exception as e:
            print("删除失败", e)

    def add(self, table, field_dict):
        print("field_dict is", field_dict)
        command = f"insert into {table}(%%fields%%) values(%%fields_value%%);"
        fields,fields_value = "", ""
        for i, each_field in enumerate(field_dict):
            if i==len(field_dict)-1:
                fields += each_field
                fields_value += f"'{field_dict[each_field]}'"
            else:
                fields += each_field +","
                fields_value += f"'{field_dict[each_field]}'" + ","
        command = command.replace(f"%%fields%%", fields)
        command = command.replace(f"%%fields_value%%", fields_value)
        # print("指令是", command)
        try:
            result_count = self.hs_mysql_cursor.execute(command)
            self.hs_mysql.commit()
        except Exception as e:
            print("添加失败", e)

    def close(self):
        self.hs_mysql_cursor.close()