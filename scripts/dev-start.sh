#!/bin/bash

# VideoCraft 开发环境启动脚本
# 一键启动前后端服务

set -e

echo "🚀 启动 VideoCraft 开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 检查依赖
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}错误: 未找到 $1，请先安装${NC}"
        exit 1
    fi
}

echo "📦 检查依赖..."
check_dependency node
check_dependency npm
check_dependency python
check_dependency pip

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p "$PROJECT_ROOT/backend/uploads"
mkdir -p "$PROJECT_ROOT/backend/logs"

# 检查环境变量文件
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，使用 .env.example 创建...${NC}"
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo -e "${YELLOW}请编辑 .env 文件配置豆包 API Key${NC}"
fi

# 启动后端
echo "🔧 启动后端服务..."
cd "$PROJECT_ROOT/backend"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装后端依赖..."
pip install -q -r requirements.txt

# 启动后端服务（后台运行）
echo "启动后端服务 (http://localhost:8000)..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 启动前端
echo "🎨 启动前端服务..."
cd "$PROJECT_ROOT/frontend"

# 安装依赖（如果 node_modules 不存在）
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端服务
echo "启动前端服务 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"

# 输出访问信息
echo ""
echo -e "${GREEN}🎉 VideoCraft 开发环境启动成功！${NC}"
echo ""
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap 'echo -e "\n${YELLOW}正在停止服务...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# 等待
wait
