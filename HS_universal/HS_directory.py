directory
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
        # 系统用户目录
        self.system_user_path = os.path.expanduser("~")
        # 文稿目录
        self.document_path = os.path.join(self.system_user_path, "Documents")
        # 本工具数据存放路径
        self.tool_data_path = os.path.join(self.system_user_path, "HS_tool")
        # 配置文件路径
        self.config_dir = self.define_path(os.path.join(self.tool_data_path, "Config"))
        # 文件下载路径
        self.File = self.define_path(os.path.join(self.tool_data_path, "File"))
        # 默认头像路径
        self.default_avatar = os.path.join(self.tool_picture_dir, "default_avatar.png")
        # 帮助文档路径
        self.help_document = os.path.join(self.tool_home_dir, "Resource/HealthSensingTool_doc.pdf")

    @property
    def tool_home_dir(self):
        # 应当返回HS_tool.py 所在路径
        init_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))) # py2app
        if "HS_tool.py" in os.listdir(init_path):
            return init_path
        else:
            init_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            # print("++++++", init_path, os.listdir(init_path))
            if "HS_tool.py" in os.listdir(init_path):
                return init_path
            else:
                return self.tool_data_path

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
                if ":" in path[2:]:  # and path.find(":") != 1: 盘符不用替换
                    path = path[:2] + path[2:].replace(":", "_")
                print(path)
            os.makedirs(path, exist_ok=True)
        return path

    @property
    def tool_picture_dir(self):
        return self.define_path(os.path.join(self.tool_home_dir, f"Resource/Image"))

    @property
    def user_avartar_dir(self):
        return self.define_path(os.path.join(self.tool_data_path, f"Avatar"))

    def read_user_info_file(self, account):
        '''
        user_info = {"account": {"name":"xxx", "sign":"xxx", "photo":"xxx", ... "friend_dict":{}...}}
        '''
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
        # print("写入前信息", old_user_info)
        old_user_info.update(user_info)
        for path in [user_info_path, current_user_path]:
            with open(path, "wb") as f:
                try:
                    # print("写入后信息", old_user_info)
                    pickle.dump(old_user_info, f)
                except Exception as e:
                    print(f"保存用户数据文件出错", str(e))

    def user_file_dir(self, from_account, target_account=""):
        save_path = os.path.join(self.File, f"{from_account + os.sep + target_account}")
        return self.define_path(save_path)

