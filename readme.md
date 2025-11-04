# 橘雪莉表情包生成器

一个基于FastAPI的表情包生成后端服务，可以快速生成带有自定义文字的橘雪莉表情包。

## 项目特点
- 支持多种橘雪莉表情模板，也可以自行扩展
- 文字自动居中且带黑色描边，确保在任何背景下清晰可见
- 简单易用的 API 接口
- 自动清理临时生成的图片，节省存储空间
- 完整的配置系统，支持自定义字体和资源路径

## 项目结构
```
├── api/ # API接口定义
├── core/ # 核心配置和初始化
├── data/ # 数据存储
│ ├── conf/ # 配置文件
│ ├── log.txt # 日志文件
│ └── memes/ # 生成的表情包存储 
├── doc/ # 文档文件
├── drawer/ # 表情包绘制逻辑
├── resource/ # 资源文件 
│ ├── fonts/ # 字体文件 
│ └── *.png # 表情模板图片 
├── utils/ # 工具类 
│ ├── conf.py # 配置管理 
│ └── log.py # 日志系统 
├── main.py # 程序入口 
├── requirements.txt # 依赖包列表 
└── readme.md # 项目说明文档
```
## 环境要求
- Python 3.10+
- pip

## 快速开始

### 1. 克隆项目
```bash
git clone [项目地址]
cd ShyeriMeme
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行服务
```bash
python main.py
```
服务将在 `http://0.0.0.0:7210` 启动

## 配置说明
配置文件位于 `data/conf/conf.json`，可以修改以下参数：

```json
{
  "name": "ShyeriMeme",
  "work_dir": "./",
  "log": {
    "log_level": "info",
    "output_path": "data/",
    "output_file": "log.txt"
  },
  "api": {
    "route_root": "/",
    "port": 7210,
    "host": "0.0.0.0",
    "token": "",
    "domain": "www.example.com"
  },
  "resource": {
    "resource_paths": {
      "哭": "resource/shyeri_cry.png",
      "慌张": "resource/shyeri_fear.png",
      "点赞": "resource/shyeri_good.png",
      "震惊": "resource/shyeri_shocked.png",
      "惊讶": "resource/shyeri_surprise.png",
      "灵机一动": "resource/shyeri_ting.png",
      "好吃": "resource/shyeri_yummy.png",
      "愣住": "resource/shyeri_speechless.png",
      "恍悟": "resource/shyeri_soga.png",
      "得意": "resource/shyeri_proud.png"
    },
    "chinese_font_path": "resource/fonts/STHeitiMedium.ttc",
    "english_font_path": "resource/fonts/Times New Roman.ttf"
  }
}
```
由于 api 返回的是图片的 url，所以需要配置域名，否则无法访问图片。
配置文件中 `api.domain` 项需要设置为你的域名，例如 `www.example.com`。

## API 文档

### 生成表情包
- **URL**: `/shyeri_meme/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **请求参数**:

| 参数名        | 类型     | 必需 | 说明                                        |
|------------|--------|----|-------------------------------------------|
| background | string | 是  | 表情模板名称，可选值：哭、慌张、点赞、震惊、惊讶、灵机一动、好吃、愣住、恍悟、得意 |
| text       | string | 是  | 要添加到表情包上的文字                               |

- **请求示例**:
```json
{
  "background": "得意",
  "text": "我一根手指就能扣晕你"
}
```

- **返回示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "img_url": "http://www.example.com:7210/images/shyeri_meme_得意_我一根手指就能扣晕你.jpg"
  }
}
```

- **图片示例**:
![shyeri_meme_得意_我一根手指就能扣晕你.jpg](doc/shyeri_meme_%E5%BE%97%E6%84%8F_%E6%88%91%E4%B8%80%E6%A0%B9%E6%89%8B%E6%8C%87%E5%B0%B1%E8%83%BD%E6%89%A3%E6%99%95%E4%BD%A0.jpg)

- **错误响应**:
  - 400: 请求参数错误或背景图不存在
  - 500: 服务器内部错误

### 获取背景图片列表
- **URL**: `/shyri_meme/list`
- **Method**: GET
- **描述**: 获取所有可用的背景图片关键字列表
- **返回示例**:
```json
{
  "code": 200,
  "message": "success",
  "data":  {
    "backgrounds": ["哭", "慌张", "点赞", "震惊", "惊讶", "灵机一动", "好吃", "愣住", "恍悟", "得意"],
    "total": 10
  }

}
```

- **错误响应**:
  - 500: 服务器内部错误

### 访问生成的图片
生成的图片可以通过返回的 `img_url` 直接访问，图片会在生成后5分钟自动删除。

## 字体说明
项目默认使用以下字体：
- 中文字体：STHeitiMedium.ttc
- 英文字体：Times New Roman.ttf

可以在配置文件中修改字体路径。

## 日志系统
日志文件位于 `data/log.txt`，记录了系统运行状态和错误信息。

## 常见问题

### 1. 为什么生成的图片在一段时间后无法访问？
为了节省存储空间，生成的图片会在5分钟后自动删除。请及时保存需要的图片。

### 2. 如何添加新的表情模板？
1. 将新的表情图片放入 `resource/` 目录
2. 在配置文件中的 `resource.resource_paths` 中添加对应的映射关系

### 3. 如何修改文字样式？
可以修改 `drawer/meme_draw.py` 文件中的 `_draw_centered_text` 方法来自定义文字样式，包括颜色、大小、描边等。

## 许可证
[MIT License](LICENSE)