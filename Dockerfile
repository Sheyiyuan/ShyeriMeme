FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 添加项目文件
COPY . /app

# 设置环境变量
ENV WORK_DIR=/app

# 创建正确的数据目录结构
RUN mkdir -p /app/data/conf /app/data/memes /app/data/log

# 添加卷声明，实现数据持久化
VOLUME /app/data

# 暴露API端口（根据core.py中的配置修改为7210）
EXPOSE 7210

# 设置启动命令
CMD ["python", "main.py"]