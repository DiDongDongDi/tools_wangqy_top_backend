#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本目录的上级目录）
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "正在重启Django服务..."

# 切换到项目目录
cd "$PROJECT_DIR/src"

# 查找并杀死现有的Django进程
echo "停止现有服务..."
pkill -f "manage.py runserver" || true

# 等待进程完全停止
sleep 2

# 创建日志目录（在项目根目录下）
mkdir -p "$PROJECT_DIR/logs"

# 设置日志文件路径
LOG_FILE="$PROJECT_DIR/logs/django.log"

# 在启动服务前进行日志轮转检查
echo "检查日志轮转..."
"$SCRIPT_DIR/log_rotate.sh"

# 启动新的Django服务
echo "启动新服务..."
# 启动Django服务并将日志输出到文件
python manage.py runserver >>"$LOG_FILE" 2>&1 &

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if pgrep -f "manage.py runserver" >/dev/null; then
    echo "✅ Django服务已成功重启"
    echo "服务运行在: http://127.0.0.1:8000/"

    # 设置定时日志轮转任务（每小时检查一次）
    echo "设置定时日志轮转任务..."
    setup_log_rotation() {
        # 创建crontab条目
        CRON_JOB="0 * * * * $SCRIPT_DIR/log_rotate.sh >> $PROJECT_DIR/logs/log_rotate.log 2>&1"

        # 检查是否已经存在相同的crontab条目
        if ! crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR/log_rotate.sh"; then
            # 添加新的crontab条目
            (
                crontab -l 2>/dev/null
                echo "$CRON_JOB"
            ) | crontab -
            echo "✅ 定时日志轮转任务已设置（每小时执行一次）"
        else
            echo "ℹ️  定时日志轮转任务已存在"
        fi
    }

    # 尝试设置定时任务
    setup_log_rotation

    echo ""
    echo "📋 日志管理信息:"
    echo "   - 当前日志文件: $LOG_FILE"
    echo "   - 日志轮转脚本: $SCRIPT_DIR/log_rotate.sh"
    echo "   - 轮转配置: 最大100MB，保留5个文件"
    echo "   - 定时任务: 每小时检查一次"
    echo "   - 手动轮转: $SCRIPT_DIR/log_rotate.sh"
else
    echo "❌ 服务启动失败"
    exit 1
fi
