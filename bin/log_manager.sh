#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本目录的上级目录）
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 日志文件路径
LOG_FILE="$PROJECT_DIR/logs/django.log"

# 显示帮助信息
show_help() {
    echo "Django日志管理工具"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  status     - 显示日志状态信息"
    echo "  tail       - 实时查看日志（最后50行）"
    echo "  tail -n N  - 查看最后N行日志"
    echo "  rotate     - 手动执行日志轮转"
    echo "  clean      - 清理所有日志文件"
    echo "  stats      - 显示日志统计信息"
    echo "  help       - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status"
    echo "  $0 tail"
    echo "  $0 tail -n 100"
    echo "  $0 rotate"
    echo "  $0 clean"
}

# 显示日志状态
show_status() {
    echo "📊 日志状态信息"
    echo "=================="
    echo "日志目录: $PROJECT_DIR/logs"
    echo "主日志文件: $LOG_FILE"
    echo ""

    if [ -f "$LOG_FILE" ]; then
        local size=$(du -h "$LOG_FILE" | cut -f1)
        local lines=$(wc -l <"$LOG_FILE" 2>/dev/null || echo "0")
        local last_modified=$(stat -f "%Sm" "$LOG_FILE" 2>/dev/null || stat -c "%y" "$LOG_FILE" 2>/dev/null || echo "未知")

        echo "主日志文件状态:"
        echo "  - 大小: $size"
        echo "  - 行数: $lines"
        echo "  - 最后修改: $last_modified"
    else
        echo "主日志文件: 不存在"
    fi

    echo ""
    echo "轮转日志文件:"
    local found_rotated=false
    for i in {1..5}; do
        if [ -f "${LOG_FILE}.${i}" ]; then
            local size=$(du -h "${LOG_FILE}.${i}" | cut -f1)
            local lines=$(wc -l <"${LOG_FILE}.${i}" 2>/dev/null || echo "0")
            echo "  - ${LOG_FILE}.${i}: $size ($lines 行)"
            found_rotated=true
        fi
    done

    if [ "$found_rotated" = false ]; then
        echo "  - 无轮转日志文件"
    fi

    echo ""
    echo "定时任务状态:"
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR/log_rotate.sh"; then
        echo "  ✅ 定时日志轮转已启用"
        crontab -l 2>/dev/null | grep "$SCRIPT_DIR/log_rotate.sh"
    else
        echo "  ❌ 定时日志轮转未启用"
    fi
}

# 实时查看日志
tail_log() {
    local lines=${1:-50}
    echo "📋 查看最后 ${lines} 行日志"
    echo "=================="

    if [ -f "$LOG_FILE" ]; then
        tail -n "$lines" "$LOG_FILE"
    else
        echo "日志文件不存在: $LOG_FILE"
    fi
}

# 显示日志统计信息
show_stats() {
    echo "📈 日志统计信息"
    echo "=================="

    if [ -f "$LOG_FILE" ]; then
        echo "主日志文件统计:"
        echo "  - 总行数: $(wc -l <"$LOG_FILE")"
        echo "  - 文件大小: $(du -h "$LOG_FILE" | cut -f1)"
        echo "  - 错误数量: $(grep -i "error\|exception\|traceback" "$LOG_FILE" | wc -l)"
        echo "  - 警告数量: $(grep -i "warning" "$LOG_FILE" | wc -l)"
        echo "  - 请求数量: $(grep -i "GET\|POST\|PUT\|DELETE" "$LOG_FILE" | wc -l)"

        echo ""
        echo "最近24小时活动:"
        local yesterday=$(date -v-1d +"%Y-%m-%d" 2>/dev/null || date -d "1 day ago" +"%Y-%m-%d" 2>/dev/null)
        echo "  - 今日日志行数: $(grep "$(date +%Y-%m-%d)" "$LOG_FILE" | wc -l)"
        echo "  - 昨日日志行数: $(grep "$yesterday" "$LOG_FILE" | wc -l)"
    else
        echo "日志文件不存在"
    fi
}

# 清理所有日志文件
clean_logs() {
    echo "🧹 清理所有日志文件"
    echo "=================="

    echo "警告: 这将删除所有日志文件！"
    read -p "确认继续? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除主日志文件
        if [ -f "$LOG_FILE" ]; then
            rm "$LOG_FILE"
            echo "✅ 已删除主日志文件"
        fi

        # 删除轮转日志文件
        local deleted_count=0
        for i in {1..10}; do
            if [ -f "${LOG_FILE}.${i}" ]; then
                rm "${LOG_FILE}.${i}"
                deleted_count=$((deleted_count + 1))
            fi
        done

        if [ $deleted_count -gt 0 ]; then
            echo "✅ 已删除 $deleted_count 个轮转日志文件"
        fi

        # 删除日志轮转脚本的日志
        if [ -f "$PROJECT_DIR/logs/log_rotate.log" ]; then
            rm "$PROJECT_DIR/logs/log_rotate.log"
            echo "✅ 已删除日志轮转脚本日志"
        fi

        echo "✅ 所有日志文件已清理"
    else
        echo "❌ 操作已取消"
    fi
}

# 主程序逻辑
case "${1:-help}" in
"status")
    show_status
    ;;
"tail")
    if [ "$2" = "-n" ] && [ -n "$3" ]; then
        tail_log "$3"
    else
        tail_log 50
    fi
    ;;
"rotate")
    echo "🔄 手动执行日志轮转"
    echo "=================="
    "$SCRIPT_DIR/log_rotate.sh"
    ;;
"clean")
    clean_logs
    ;;
"stats")
    show_stats
    ;;
"help" | *)
    show_help
    ;;
esac
