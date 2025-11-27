#!/bin/bash
# Linus式启动：一行搞定

nohup python3 src/main.py > /dev/null 2>&1 & echo $! > server.pid
echo "✅ 服务器已启动 (PID: $(cat server.pid))"