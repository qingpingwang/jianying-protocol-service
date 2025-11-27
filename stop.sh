#!/bin/bash
# Linus式停止：读pid，kill，删除

kill $(cat server.pid) && rm server.pid
echo "✅ 服务器已停止"
