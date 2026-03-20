#!/bin/bash
# Media Player v2.0 启动脚本
# 使用 Python 3.11 虚拟环境

cd ~/media-player

# 激活虚拟环境
source .venv/bin/activate

echo "🚀 启动 Media Player v2.0"
echo ""

# 检查端口
if lsof -i:8000 >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用，正在清理..."
    fuser -k 8000/tcp 2>/dev/null
    sleep 1
fi

if lsof -i:5173 >/dev/null 2>&1; then
    echo "⚠️  端口 5173 已被占用，正在清理..."
    fuser -k 5173/tcp 2>/dev/null
    sleep 1
fi

# 启动后端
echo "📦 启动后端 API..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# 启动前端
echo "🎨 启动前端开发服务器..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 服务已启动:"
echo "   📱 前端: http://localhost:5173"
echo "   🔧 后端 API: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待任意子进程退出
wait