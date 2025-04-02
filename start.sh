#!/bin/bash

# 启动后端
echo "启动后端服务..."
python app.py &
BACKEND_PID=$!

echo "等待后端启动..."
sleep 2

# 启动前端
echo "启动前端服务..."
cd frontend && npm run dev &
FRONTEND_PID=$!

# 捕获终止信号，关闭前端和后端进程
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# 等待
wait 