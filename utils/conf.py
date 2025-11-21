import json
import os

class Config:
    PATH = "./data/conf"
    FILE = "conf.json"
    def __init__(self, path:str=PATH, file:str=FILE, default:dict=None):
        if default is None:
            default = {}
        self.path = path
        self.file = file
        self.conf = default
        self.load()
    def load(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(os.path.join(self.path,self.file)):
            with open(os.path.join(self.path,self.file),"w") as f:
                json.dump(self.conf, f, indent=2, ensure_ascii=False)
        with open(os.path.join(self.path,self.file)) as f:
            self.conf = json.load(f)
    def save(self):
        with open(os.path.join(self.path,self.file),"w") as f:
            json.dump(self.conf, f, indent=2, ensure_ascii=False)
    def get(self):
        return self.conf
    def set(self,conf:dict):
        self.conf = conf
        self.save()