#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本目录的上级目录）
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 日志文件路径
LOG_FILE="$PROJECT_DIR/logs/django.log"
# 日志轮转配置
MAX_SIZE_MB=100  # 最大文件大小（MB）
MAX_FILES=5      # 保留的日志文件数量

echo "开始日志轮转检查..."

# 检查日志文件是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "日志文件不存在: $LOG_FILE"
    exit 0
fi

# 获取当前日志文件大小（MB）
current_size=$(du -m "$LOG_FILE" | cut -f1)

echo "当前日志文件大小: ${current_size}MB"

# 如果文件大小超过限制，进行轮转
if [ "$current_size" -gt "$MAX_SIZE_MB" ]; then
    echo "日志文件大小超过 ${MAX_SIZE_MB}MB，开始轮转..."
    
    # 删除最旧的日志文件（如果存在）
    if [ -f "${LOG_FILE}.${MAX_FILES}" ]; then
        rm "${LOG_FILE}.${MAX_FILES}"
        echo "删除最旧的日志文件: ${LOG_FILE}.${MAX_FILES}"
    fi
    
    # 轮转现有的日志文件
    for i in $(seq $((MAX_FILES-1)) -1 1); do
        if [ -f "${LOG_FILE}.${i}" ]; then
            mv "${LOG_FILE}.${i}" "${LOG_FILE}.$((i+1))"
            echo "轮转日志文件: ${LOG_FILE}.${i} -> ${LOG_FILE}.$((i+1))"
        fi
    done
    
    # 重命名当前日志文件
    mv "$LOG_FILE" "${LOG_FILE}.1"
    echo "轮转当前日志文件: $LOG_FILE -> ${LOG_FILE}.1"
    
    # 创建新的日志文件
    touch "$LOG_FILE"
    echo "创建新的日志文件: $LOG_FILE"
    
    # 重新加载Django进程的日志输出（如果进程正在运行）
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo "重新加载Django进程的日志输出..."
        # 这里可以发送信号给Django进程重新打开日志文件
        # 或者简单地记录轮转完成
        echo "$(date): 日志轮转完成" >> "$LOG_FILE"
    fi
    
    echo "✅ 日志轮转完成"
else
    echo "日志文件大小正常，无需轮转"
fi

echo "日志轮转检查完成" 