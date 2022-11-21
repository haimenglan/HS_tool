import os
import sys
import platform
import time
import pickle

class HS_directory:
    def __init__(self):
        '''
        定义
        1. 用户配置文件目录Config，保存用户配置文件account_setting，保存用户信息account_info
        2. 软件所需图片目录Image
        3. 用户头像目录Image/Avatar, 所有头像都保存在这个下面
        4. 发送文件目录File
        '''
        self.system_user_path = os.path.expanduser("~")
        print("系统用户家目录", self.system_user_path) # /users/js-15400155
        self.config_dir = self.define_path(os.path.join(os.path.dirname(__file__),"Config"))
        print("配置目录", self.config_dir)
        self.File = self.define_path( os.path.join(os.path.dirname(__file__), "File"))

        self.default_avatar = os.path.join(self.tool_picture_dir, "Avatar/default_avatar.png")
        self.help_document = os.path.join(self.tool_home_dir, "HealthSensingTool 说明文档.pdf")

    @property
    def tool_home_dir(self):  # /Users/js-15400155/Desktop/HS_tool_env/HS_4.0.1
        check_file_list = ["main.py"]
        init_path = os.path.dirname(os.path.realpath(__file__))
        print("我的位置是", init_path)
        current_time = time.time()
        while len(check_file_list) > 0 and time.time() - current_time < 20:
            for path, include_directory, include_files in os.walk(init_path):
                for each_name in check_file_list:
                    if each_name in include_files:
                        return path
                    if len(check_file_list) == 0:
                        break
                if len(check_file_list) == 0:
                    break
            # 如果当前执行文件的目录找不到，则到上层目录找
            init_path = os.path.dirname(init_path)
            if init_path == "":
                return sys.path[0]

    def delete_file(self,path):
        # print("删除文件")
        os.remove(path)
        current_dir = os.path.dirname(path)
        try:
            os.removedirs(current_dir)
        except:
            pass

    def define_path(self, path):
        if not os.path.exists(path):
            if platform.system() == "Windows":
                print("替换冒号，妈的")
                if ":" in path[2:]:  # and path.find(":") != 1: 盘符不用替换
                    path = path[:2] + path[2:].replace(":", "_")
                print(path)
            os.makedirs(path, exist_ok=True)
        return path

    @property
    def tool_picture_dir(self):
        return self.define_path(os.path.join(self.tool_home_dir, f"Image"))

    @property
    def user_avartar_dir(self):
        return self.define_path(os.path.join(self.tool_picture_dir, f"Avatar"))

    def read_user_info_file(self, account):
        user_info = {}
        if account:
            user_info_path = os.path.join(self.config_dir, account)
        else:
            user_info_path = os.path.join(self.config_dir, "current_user")
        if os.path.exists(user_info_path):
            with open(user_info_path, "rb") as f:
                try:
                    user_info = pickle.load(f)
                except Exception as e:
                    print(f"读取用户数据文件出错", str(e))
        return user_info

    def write_user_info_file(self, account, user_info):
        '''
        将我的信息写入本地文件
        '''
        user_info_path = os.path.join(self.config_dir, account)
        current_user_path = os.path.join(self.config_dir, "current_user")
        old_user_info = self.read_user_info_file(account)
        old_user_info.update(user_info)
        for path in [user_info_path, current_user_path]:
            with open(path, "wb") as f:
                try:
                    pickle.dump(old_user_info, f)
                except Exception as e:
                    print(f"保存用户数据文件出错", str(e))

    def user_file_dir(self, from_account, target_account):
        save_path = os.path.join(self.File, f"{from_account + os.sep + target_account}")
        return self.define_path(save_path)