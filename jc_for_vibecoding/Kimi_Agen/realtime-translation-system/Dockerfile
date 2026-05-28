# 实时语音转录翻译系统 Docker 镜像
# 基于 CUDA 12.4 + Python 3.12

FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# 环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    git \
    wget \
    curl \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python 3.12 为默认
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# 升级 pip
RUN python -m pip install --upgrade pip setuptools wheel

# 创建工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY backend/ ./backend/
COPY config.yaml .
COPY start.sh .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "-m", "backend.server"]
