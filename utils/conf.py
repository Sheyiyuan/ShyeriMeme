import json
import os

class Config:
    PATH = "./data/conf"
    FILE = "conf.json"
    def __init__(self, path:str=PATH, file:str=FILE, default:dict=None):
        if default is None or default == {}:
            default = {}
        self.path = path
        self.file = file
        self.default = default  # 保存默认配置
        self.conf = default.copy()  # 初始化为默认配置的副本
        self.load()
    
    def _deep_merge(self, target, source):
        """深度合并两个字典，source中的值会覆盖target中的同名值"""
        if isinstance(target, dict) and isinstance(source, dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    self._deep_merge(target[key], value)
                else:
                    target[key] = value
        return target
    
    def load(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        file_path = os.path.join(self.path, self.file)
        
        if not os.path.exists(file_path):
            # 如果配置文件不存在，保存默认配置
            with open(file_path, "w") as f:
                json.dump(self.default, f, indent=2, ensure_ascii=False)
            self.conf = self.default.copy()
        else:
            # 如果配置文件存在，读取并与默认配置合并
            with open(file_path) as f:
                file_config = json.load(f)
            
            # 深度合并默认配置和文件配置（文件配置优先级高）
            merged_config = self._deep_merge(self.default.copy(), file_config)
            self.conf = merged_config
            
            # 将合并后的完整配置写回文件
            with open(file_path, "w") as f:
                json.dump(merged_config, f, indent=2, ensure_ascii=False)
    
    def save(self):
        with open(os.path.join(self.path, self.file), "w") as f:
            json.dump(self.conf, f, indent=2, ensure_ascii=False)
    
    def get(self):
        return self.conf
    
    def set(self, conf:dict):
        self.conf = conf
        self.save()