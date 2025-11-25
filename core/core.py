from utils.conf import Config
from utils.log import Logos

DEFAULT_CONFIG = {
    "name":"ShyeriMeme",
    "work_dir":"./",
    "log":{
        "log_level":"info",
        "output_path":"data/",
        "output_file":"log.txt"
    },
    "api":{
        "route_root":"/",
        "port":7210,
        "host":"0.0.0.0",
        "token":"",
        "domain":"127.0.0.1:7210"
    },
    "resource":{
        "resource_paths":{
            "得意":"resource/shyeri_proud.png",
            "哭":"resource/shyeri_cry.png",
            "慌张":"resource/shyeri_fear.png",
            "点赞":"resource/shyeri_good.png",
            "震惊":"resource/shyeri_shocked.png",
            "害羞":"resource/shyeri_shy.png",
            "投降":"resource/shyeri_surrender.png",
            "惊讶":"resource/shyeri_surprise.png",
            "灵机一动":"resource/shyeri_ting.png",
            "好吃":"resource/shyeri_yummy.png",
            "愣住":"resource/shyeri_speechless.png",
            "恍悟":"resource/shyeri_soga.png",
        },
        "chinese_font_path":"resource/fonts/STHeitiMedium.ttc",
        "english_font_path":"resource/fonts/Times New Roman.ttf"
    },
    "storage":{
        "image_expiry_time": 300
    }
}

conf = Config(default=DEFAULT_CONFIG)
log = Logos(name=conf.get()["name"], level=conf.get()["log"]["log_level"].upper(),output_path= conf.get()["work_dir"]+conf.get()["log"]["output_path"],output_file=conf.get()["log"]["output_file"])