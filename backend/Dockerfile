# backend/Dockerfile
FROM python:3.12.0-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（sentence-transformers 编译需要）
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，利用 Docker 层缓存加速
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 预下载 embedding 模型（可选，加快首次启动；但会让镜像变大 100MB+）
# 如果不想让镜像太大，可以注释掉下面这行，改为运行时下载
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]