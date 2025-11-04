import asyncio
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sys
import threading
import time
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from core.core import conf,log
from drawer.meme_draw import CertificateGenerator


shyeri_meme_app = FastAPI()
bg_paths: dict[str, str] = conf.get()["resource"]["resource_paths"]
chinese_font_path = conf.get()["resource"]["chinese_font_path"]
english_font_path = conf.get()["resource"]["english_font_path"]
ShyeriMemeDrawer = CertificateGenerator(
    log=log,
    resource_paths= bg_paths,
    output_folder = "data/memes",
    chinese_font_path=chinese_font_path,
    english_font_path=english_font_path
)

file = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(file, "../")
IMAGE_FOLDER = path + "data/memes"
DOMAIN = conf.get()["api"]["domain"]
PORT = conf.get()["api"]["port"]

@shyeri_meme_app.post("/shyeri_meme/")
async def shyeri_meme_deal(request: Request):
    try:
        form_data = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "请求体必须包含有效的JSON数据",
                "data": {}
            }
        )

    # 检查必需字段是否存在
    if not all(key in form_data for key in ["background", "text"]):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "请求必须包含background和text字段",
                "data": {}
            }
        )

    background = form_data["background"]
    text = form_data["text"]
    # 检查背景图是否存在
    if background not in bg_paths:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": f"请求必须包含有效的background字段，可选值为{list(bg_paths.keys())}",
                "data": {}
            }
        )
    try:
        ShyeriMemeDrawer.generate_meme(
            resource=background,
            text=text,
        )
    except Exception as e:
        log.error(f"生成表情包{background}_{text}时出错: {e}")
        print(f"生成表情包{background}_{text}时出错: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message":f"请求出错：{e}",
                "data": {}
            }
        )
    create_image_and_start_deletion(f"shyeri_meme_{background}_{text}.jpg")
    return JSONResponse(
    status_code=200,
    content={
        "code": 200,
        "message": "success",
        "data": {
            "img_url": f"http://{DOMAIN}:{PORT}/images/shyeri_meme_{background}_{text}.jpg",
        }
    })


# 添加获取可用背景关键字列表的接口
@shyeri_meme_app.get("/shyri_meme/list")
async def get_background_list():
    """获取所有可用的背景图片关键字列表
    
    返回值：
        JSONResponse: 包含背景关键字列表的响应
    """
    try:
        # 从配置中获取所有背景关键字
        background_list = list(bg_paths.keys())
        
        # 记录日志
        log.info(f"获取背景列表成功，共{len(background_list)}个背景")
        
        # 返回响应
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success",
                "data": {
                    "background_list": background_list,
                    "total": len(background_list)
                }
            }
        )
    except Exception as e:
        # 记录错误日志
        log.error(f"获取背景列表失败: {e}")
        print(f"获取背景列表失败: {e}")
        
        # 返回错误响应
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"获取背景列表失败: {e}",
                "data": {}
            }
        )

# 挂载静态目录
shyeri_meme_app.mount("/images", StaticFiles(directory=IMAGE_FOLDER), name="images")

# 启动定时删除线程
def delete_file(path):
    time.sleep(300)  # 等待300秒
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"已删除图片: {path}")
    except Exception as e:
        print(f"删除图片失败: {e}")


# 模拟文件创建时启动删除线程
def create_image_and_start_deletion(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    threading.Thread(target=delete_file, args=(image_path,)).start()

# 添加全局异常处理中间件
@shyeri_meme_app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # 设置全局超时
        return await asyncio.wait_for(call_next(request), timeout=30)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "请求超时"}, status_code=504)