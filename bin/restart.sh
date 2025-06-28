#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本目录的上级目录）
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 导入配置文件
source "$SCRIPT_DIR/config.sh"

# 默认环境为生产环境
ENVIRONMENT="prd"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        dev)
            ENVIRONMENT="dev"
            shift
            ;;
        prd)
            ENVIRONMENT="prd"
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [dev|prd]"
            echo "  dev - 开发环境"
            echo "  prd - 生产环境 (默认)"
            exit 1
            ;;
    esac
done

# 根据环境设置Python可执行命令路径和Django设置
PYTHON_CMD=$(get_python_cmd "$ENVIRONMENT")
SETTINGS_MODULE=$(get_settings_module "$ENVIRONMENT")
ENV_DESCRIPTION=$(get_env_description "$ENVIRONMENT")

echo "🔧 使用${ENV_DESCRIPTION}配置"
echo "正在重启Django服务 (环境: $ENVIRONMENT)..."

# 切换到项目目录
cd "$PROJECT_DIR/django_base"

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
# 设置Django环境变量并启动服务
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
$PYTHON_CMD manage.py runserver 2>&1 | tee "$LOG_FILE" &

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
    echo "   - 当前环境: $ENVIRONMENT ($ENV_DESCRIPTION)"
    echo "   - Python命令: $PYTHON_CMD"
    echo "   - Django设置模块: $SETTINGS_MODULE"
    echo "   - 当前日志文件: $LOG_FILE"
    echo "   - 日志轮转脚本: $SCRIPT_DIR/log_rotate.sh"
    echo "   - 轮转配置: 最大100MB，保留5个文件"
    echo "   - 定时任务: 每小时检查一次"
    echo "   - 手动轮转: $SCRIPT_DIR/log_rotate.sh"
else
    echo "❌ 服务启动失败"
    exit 1
fi
