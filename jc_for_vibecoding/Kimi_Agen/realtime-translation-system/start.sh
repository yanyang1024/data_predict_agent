#!/bin/bash
# 实时语音转录翻译系统启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="asr-translation"
LOG_FILE="${SCRIPT_DIR}/logs/server.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查 Python 版本
check_python() {
    log_step "检查 Python 版本..."
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python3，请先安装"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python 版本: ${PYTHON_VERSION}"
}

# 检查 CUDA
check_cuda() {
    log_step "检查 CUDA..."
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    else
        log_warn "未找到 nvidia-smi，确保 CUDA 已安装"
    fi
}

# 检查并创建虚拟环境
setup_venv() {
    log_step "设置虚拟环境..."
    if [ ! -d "${HOME}/.venvs/${VENV_NAME}" ]; then
        log_info "创建虚拟环境..."
        mkdir -p "${HOME}/.venvs"
        python3 -m venv "${HOME}/.venvs/${VENV_NAME}"
    fi
    source "${HOME}/.venvs/${VENV_NAME}/bin/activate"
    log_info "虚拟环境已激活"
}

# 安装依赖
install_deps() {
    log_step "检查依赖..."
    pip install --upgrade pip -q

    # 检查核心包
    if ! python3 -c "import qwen_asr" 2>/dev/null; then
        log_info "安装 qwen-asr[vllm]..."
        pip install qwen-asr[vllm]
    fi

    if ! python3 -c "import fastapi" 2>/dev/null; then
        log_info "安装 FastAPI..."
        pip install fastapi uvicorn websockets
    fi

    if ! python3 -c "import openai" 2>/dev/null; then
        log_info "安装 OpenAI SDK..."
        pip install openai
    fi

    if ! python3 -c "import numpy" 2>/dev/null; then
        log_info "安装 numpy..."
        pip install numpy
    fi

    log_info "依赖检查完成"
}

# 检查模型
check_model() {
    log_step "检查模型..."
    python3 << EOF
from qwen_asr import Qwen3ASRModel
import torch

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
EOF
}

# 创建日志目录
mkdir -p "${SCRIPT_DIR}/logs"

# 主函数
main() {
    echo "========================================"
    echo "  实时语音转录翻译系统"
    echo "========================================"

    check_python
    check_cuda
    setup_venv
    install_deps
    check_model

    log_step "启动服务..."
    log_info "Dashboard: http://localhost:8080/dashboard"
    log_info "API: http://localhost:8080"
    log_info "日志: ${LOG_FILE}"
    echo "========================================"

    cd "${SCRIPT_DIR}/backend"
    exec python3 server.py 2>&1 | tee -a "${LOG_FILE}"
}

# 处理命令行参数
case "${1:-}" in
    --check)
        check_python
        check_cuda
        setup_venv
        install_deps
        check_model
        ;;
    --help|-h)
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --check    仅检查环境，不启动服务"
        echo "  --help     显示帮助"
        echo ""
        echo "默认启动服务"
        ;;
    *)
        main
        ;;
esac
