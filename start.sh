#!/bin/bash
# Web Media Player 启动脚本

cd ~/media-player

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install -r backend/requirements.txt -q

# 启动后端 + 静态文件服务
echo "🚀 启动服务..."
echo "📱 访问: http://localhost:8000"
echo ""

# 使用 uvicorn 启动，同时服务静态文件
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 使用 Python 服务前端静态文件
cd frontend && python3 -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "✅ 服务已启动:"
echo "   后端 API: http://localhost:8000/docs"
echo "   前端页面: http://localhost:8080"
echo ""
echo "按 Ctrl+C 停止服务"

wait