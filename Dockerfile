# 使用官方 Python 3.10 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 禁用 Python 生成 pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 禁用 Python 缓冲，确保日志能实时输出
ENV PYTHONUNBUFFERED 1

# 安装系统依赖 (如果需要编译某些 python 包)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 将整个 backend 目录下的内容复制到工作目录
COPY backend/ .

# 创建静态资源目录并设置权限 (确保容器有权写入)
RUN mkdir -p static/experience && chmod -R 755 static

# 暴露 FastAPI 默认运行端口
EXPOSE 8000

# 启动命令：使用 uvicorn 运行，注意路径根据你的 src.main:app 结构
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
