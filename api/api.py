# 在导入部分添加FileResponse
import asyncio
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import sys
import threading
import time
import os
import json
from pathlib import Path

from utils.log import Logos

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from core.core import conf, log
from drawer.meme_draw import CertificateGenerator


shyeri_meme_app = FastAPI()
bg_paths: dict[str, str] = conf.get()["resource"]["resource_paths"]
chinese_font_path = conf.get()["resource"]["chinese_font_path"]
english_font_path = conf.get()["resource"]["english_font_path"]
# 获取过期时间配置
IMAGE_EXPIRY_TIME = conf.get().get("storage", {}).get("image_expiry_time", 300)

ShyeriMemeDrawer = CertificateGenerator(
    log=log,
    resource_paths=bg_paths,
    output_folder="data/memes",
    chinese_font_path=chinese_font_path,
    english_font_path=english_font_path
)

file = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(file, "../")
IMAGE_FOLDER = path + "data/memes"
# 定义Vue构建后的静态文件目录
WEBUI_DIST_PATH = os.path.join(path, "webui/dist")
DOMAIN = conf.get()["api"]["domain"]
PORT = conf.get()["api"]["port"]

# 定义所有API路由
@shyeri_meme_app.post("/")
async def shyeri_meme_deal(request: Request):
    try:
        form_data = await request.json()
    except json.JSONDecodeError:
        log.error("请求体不包含有效的JSON数据")
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
        log.error("请求{data}不包含background和text字段")
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
        log.error(f"请求{background}不是有效的background字段")
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": f"请求必须包含有效的background字段，可选值为{list(bg_paths.keys())}",
                "data": {}
            }
        )
    try:
        # 调用generate_meme并获取哈希后的文件名
        image_name = ShyeriMemeDrawer.generate_meme(
            resource=background,
            text=text,
        )
    except Exception as e:
        log.error(f"生成表情包{background}_{text}时出错: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message":f"请求出错：{e}",
                "data": {}
            }
        )
    create_image_and_start_deletion(image_name)
    return JSONResponse(
    status_code=200,
    content={
        "code": 200,
        "message": "success",
        "data": {
            "img_url": f"http://{DOMAIN}/images/{image_name}",
        }
    })


# 添加获取可用背景关键字列表的接口
@shyeri_meme_app.get("/list")
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
        
        # 返回错误响应
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"获取背景列表失败: {e}",
                "data": {}
            }
        )

# 添加获取配置的接口
@shyeri_meme_app.get("/config")
async def get_config():
    return conf.get()

# 添加更新配置的接口
@shyeri_meme_app.post("/config")
async def update_config(new_config: dict = Body(...)):
    try:
        conf.set(new_config)
        # 热更新全局变量
        global bg_paths, chinese_font_path, english_font_path, IMAGE_EXPIRY_TIME, DOMAIN, PORT
        bg_paths = conf.get()["resource"]["resource_paths"]
        chinese_font_path = conf.get()["resource"]["chinese_font_path"]
        english_font_path = conf.get()["resource"]["english_font_path"]
        IMAGE_EXPIRY_TIME = conf.get().get("storage", {}).get("image_expiry_time", 300)
        DOMAIN = conf.get()["api"]["domain"]
        PORT = conf.get()["api"]["port"]
        # 重新初始化日志
        global log
        log = Logos(name=conf.get()["name"], level=conf.get()["log"]["log_level"].upper(),
                  output_path=conf.get()["work_dir"]+conf.get()["log"]["output_path"],
                  output_file=conf.get()["log"]["output_file"])
        log.info("配置已更新并热加载")
        return {"status": "success"}
    except Exception as e:
        log.error(f"更新配置失败: {e}")
        return {"status": "error", "message": str(e)}


@shyeri_meme_app.get("/background/{background_name}")
async def get_background_image(background_name: str):
    """获取指定名称的背景图片"""
    try:
        # 检查背景名称是否存在
        if background_name not in bg_paths:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "message": f"背景图片{background_name}不存在",
                    "data": {}
                }
            )

        # 获取背景图片的完整路径
        background_path = bg_paths[background_name]

        # 检查文件是否存在
        if not os.path.exists(background_path):
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "message": f"背景图片文件不存在: {background_path}",
                    "data": {}
                }
            )

        # 返回背景图片文件
        return FileResponse(background_path)
    except Exception as e:
        log.error(f"获取背景图片失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"获取背景图片失败: {e}",
                "data": {}
            }
        )

# 添加全局异常处理中间件
@shyeri_meme_app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # 设置全局超时
        return await asyncio.wait_for(call_next(request), timeout=30)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "请求超时"}, status_code=504)

# 挂载图片静态目录
shyeri_meme_app.mount("/images", StaticFiles(directory=IMAGE_FOLDER), name="images")

# 挂载Vue静态资源目录（仅用于静态文件，不使用html=True）
if os.path.exists(WEBUI_DIST_PATH):
    shyeri_meme_app.mount("/assets", StaticFiles(directory=os.path.join(WEBUI_DIST_PATH, "assets")), name="assets")
    
    # 为根路径提供index.html
    @shyeri_meme_app.get("/")
    async def serve_root():
        index_path = os.path.join(WEBUI_DIST_PATH, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"error": "Index file not found"})
    
    # 为前端路由提供index.html（关键修复）
    @shyeri_meme_app.get("/admin", include_in_schema=False)
    async def serve_admin():
        index_path = os.path.join(WEBUI_DIST_PATH, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"error": "Index file not found"})
    
    @shyeri_meme_app.get("/webui", include_in_schema=False)
    async def serve_webui():
        index_path = os.path.join(WEBUI_DIST_PATH, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"error": "Index file not found"})

shyeri_meme_app.mount("/resource", StaticFiles(directory=os.path.join(path, "resource")), name="resource")

# 工具函数
# 启动定时删除线程
def delete_file(path):
    time.sleep(IMAGE_EXPIRY_TIME)  # 使用配置中的过期时间
    try:
        if os.path.exists(path):
            os.remove(path)
            log.info(f"已删除图片: {path}")
    except Exception as e:
        log.error(f"删除图片失败: {e}")

# 模拟文件创建时启动删除线程
def create_image_and_start_deletion(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    threading.Thread(target=delete_file, args=(image_path,)).start()