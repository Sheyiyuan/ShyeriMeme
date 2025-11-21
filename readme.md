<div align="center" style="padding: 2rem; color: #2288bb; border-radius: 12px; max-width: 800px; margin: 0 auto;">

<h1 style="font-size: 2.5rem; margin-bottom: 1.5rem; font-weight: 700;">橘雪莉表情包生成器</h1>

<div style="margin-bottom: 1.5rem;">
  <a href="https://opensource.org/licenses/MIT" style="margin: 0 0.5rem;">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" style="vertical-align: middle;">
  </a>
  <a href="https://www.python.org/" style="margin: 0 0.5rem;">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python" style="vertical-align: middle;">
  </a>
  <a href="https://fastapi.tiangolo.com/" style="margin: 0 0.5rem;">
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI" style="vertical-align: middle;">
  </a>
  <a href="https://www.docker.com/" style="margin: 0 0.5rem;">
    <img src="https://img.shields.io/badge/Docker-blue.svg" alt="Docker" style="vertical-align: middle;">
  </a>
</div>

<p style="font-size: 1.2rem; color: #1177aa; font-weight: bold; margin: 1.5rem 0;">简单·快速·低占用</p>

<p style="font-size: 1rem; line-height: 1.6; max-width: 600px; margin: 0 auto 2rem;">一个基于 FastAPI 的表情包生成后端服务，可以快速生成带有自定义文字的橘雪莉表情包。</p>

<img src="doc/shyeri_meme_75f0fa966d8246d1ba25faa636a40753_8073408ba00230cdb70801db79cc3a2d.jpg" alt="宣传图" width="50%" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

</div>

---
## 项目特点

- 支持多种橘雪莉表情模板，也可以自行扩展
- 文字自动居中且带黑色描边，确保在任何背景下清晰可见
- 简单易用的 API 接口
- 自动清理临时生成的图片，节省存储空间
- 完整的配置系统，支持自定义字体和资源路径

## 项目结构

```text
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
# 使用 HTTPS 协议
git clone https://github.com/Sheyiyuan/ShyeriMeme.git # HTTPS
# 或者使用 SSH 协议，如果你不知道这是什么用上面那个
git clone git@github.com:Sheyiyuan/ShyeriMeme.git # SSH

# 进入项目目录
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

## Docker部署

除了直接运行 Python 程序外，您还可以使用 Docker 来部署此项目，这将确保环境一致性并简化部署过程。

### 前提条件

- 安装Docker：[Docker官方安装指南](https://docs.docker.com/get-docker/)

### 使用方法

#### 1. 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t shyerimeme .
```

#### 2. 运行 Docker 容器

使用以下命令运行容器：

```bash
docker run -d \
  --name shyerimeme \
  -p 7210:7210 \
  -v $(pwd)/data:/app/data \
  shyerimeme
```

参数说明：
- `-d`：后台运行容器
- `--name shyerimeme`：设置容器名称为 `shyerimeme`
- `-p 7210:7210`：将容器的7210端口映射到主机的7210端口
- `-v $(pwd)/data:/app/data`：挂载数据卷，实现数据持久化

#### 3. 使用 Docker Compose（可选）

您也可以创建一个 `docker-compose.yml` 文件来管理容器：

```yaml
version: '3'
services:
  shyerimeme:
    build: .
    container_name: shyerimeme
    ports:
      - "7210:7210"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

然后使用以下命令启动服务：

```bash
docker-compose up -d
```

### Docker 部署注意事项

1. **配置文件位置**：
   - 容器内部的配置文件位于 `/app/data/conf/conf.json`
   - 通过数据卷挂载，您可以在宿主机上直接修改 `./data/conf/conf.json`

2. **字体支持**：
   - Docker 镜像中已包含字体支持，可以正常显示中文
   - 如果需要使用自定义字体，请确保字体文件位于正确的路径

3. **数据持久化**：
   - 通过挂载 `./data` 目录，确保生成的表情包、日志和配置在容器重启后不会丢失

4. **域名配置**：
   - 在生产环境中，请确保在配置文件中设置正确的域名，以便生成可访问的图片URL

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
如果你没有域名的反向代理，你需要为 `api.domain` 项添加端口，例如 `127.0.0.1:7210`。

## API 文档

### 生成表情包

- **URL**: `/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **请求参数**:

| 参数名     | 类型   | 必需 | 说明                                                                               |
| ---------- | ------ | ---- | ---------------------------------------------------------------------------------- |
| background | string | 是   | 表情模板名称，可选值：哭、慌张、点赞、震惊、惊讶、灵机一动、好吃、愣住、恍悟、得意 |
| text       | string | 是   | 要添加到表情包上的文字                                                             |

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
<div align="center">
<img src="doc/shyeri_meme_dcd19075165d2b689b61a6a540749d61_28bccc5e3442ca5b1c74db9399fe0c99.jpg" alt="shyeri_meme_得意_我一根手指就能扣晕你.jpg" width="50%"/>
</div>

- **错误响应**:

  - 400: 请求参数错误或背景图不存在
  - 500: 服务器内部错误

### 获取背景图片列表

- **URL**: `/list`
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

生成的图片可 以通过返回的 `img_url` 直接访问，图片会在生成后根据配置的过期时间自动删除（默认5分钟）。

## 字体说明

项目默认使用以下字体：

- 中文字体：STHeitiMedium.ttc
- 英文字体：Times New Roman.ttf

可以在配置文件中修改字体路径。

## 日志系统

日志文件位于 `data/log.txt`，记录了系统运行状态和错误信息。

## 常见问题

### 1. 为什么生成的图片在一段时间后无法访问？

为了节省存储空间，生成的图片会在配置文件中设置的过期时间后自动删除（默认5分钟）。请及时保存需要的图片。

### 2. 如何添加新的表情模板？

1. 将新的表情图片放入 `resource/` 目录
2. 在配置文件中的 `resource.resource_paths` 中添加对应的映射关系

### 3. 如何修改文字样式？

可以修改 `drawer/meme_draw.py` 文件中的 `_draw_centered_text` 方法来自定义文字样式，包括颜色、大小、描边等。

## 许可证
本项目基于[MIT License](LICENSE)传播，仅供个人学习交流使用，不拥有相关素材的版权。进行分发时应注意不违反素材版权与官方二次创造协定。