import logging
import os


class Log:
    def __init__(self, log_file_path):
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w", encoding="utf8") as f:
                try:
                    f.write("创建log文件\n")
                    f.close()
                except Exception as e:
                    f.write(str(e))
                    f.close()
        # 第一步，创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # Log等级总开关
        # 第二步，创建一个handler，用于写入日志文件
        fh = logging.FileHandler(log_file_path, mode='a', encoding="utf8")  # open的打开模式这里可以进行参考
        fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        # 第三步，再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)   # 输出到console的log等级的开关
        # 第四步，定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 第五步，将logger添加到handler里面
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        # 日志总开关
        # logger.disabled = True
        self.logger.info(f'创建logger 对象')