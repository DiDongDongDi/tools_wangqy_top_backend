#!/bin/bash

# 环境配置文件
# 用于管理不同环境的Python可执行命令路径

# 开发环境配置
DEV_PYTHON_CMD="python"
DEV_SETTINGS_MODULE="src.settings"

# 生产环境配置
PRD_PYTHON_CMD="/root/.pyenv/versions/3.9.6/envs/tools_wangqy_top_backend/bin/python"
PRD_SETTINGS_MODULE="src.settings"

# 根据环境获取Python命令
get_python_cmd() {
    local env="$1"
    case "$env" in
        dev)
            echo "$DEV_PYTHON_CMD"
            ;;
        prd)
            echo "$PRD_PYTHON_CMD"
            ;;
        *)
            echo "$PRD_PYTHON_CMD"  # 默认使用生产环境配置
            ;;
    esac
}

# 根据环境获取Django设置模块
get_settings_module() {
    local env="$1"
    case "$env" in
        dev)
            echo "$DEV_SETTINGS_MODULE"
            ;;
        prd)
            echo "$PRD_SETTINGS_MODULE"
            ;;
        *)
            echo "$PRD_SETTINGS_MODULE"  # 默认使用生产环境配置
            ;;
    esac
}

# 根据环境获取环境描述
get_env_description() {
    local env="$1"
    case "$env" in
        dev)
            echo "开发环境"
            ;;
        prd)
            echo "生产环境"
            ;;
        *)
            echo "生产环境"
            ;;
    esac
} 