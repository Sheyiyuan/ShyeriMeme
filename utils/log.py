import logging
import os


class Logos:
    def __init__(self, name:str="KP-license", output_path:str="./data/", output_file:str="log.txt", level:int=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        
        # 清除已存在的处理器（避免重复添加）
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 检查输出目录是否存在，如果不存在则创建
        log_dir = os.path.dirname(os.path.join(output_path, output_file))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 正确拼接文件路径
        log_file_path = os.path.join(output_path, output_file)
        
        # 添加文件处理器
        self.handler = logging.FileHandler(log_file_path)
        self.handler.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        
        # 添加控制台处理器，方便调试
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def info(self, message:str):
        self.logger.info(message)

    def error(self, message:str):
        self.logger.error(message)

    def warning(self, message:str):
        self.logger.warning(message)

    def debug(self, message:str):
        self.logger.debug(message)

    def critical(self, message:str):
        self.logger.critical(message)