# 1. bin 目录脚本工具

本目录包含了用于管理 Django 项目的核心脚本工具，提供完整的服务管理和日志轮转功能。

## 1.1. 脚本概览

| 脚本             | 功能            | 主要用途              |
| ---------------- | --------------- | --------------------- |
| `restart.sh`     | Django 服务重启 | 开发/生产环境服务管理 |
| `log_rotate.sh`  | 日志轮转        | 自动日志文件管理      |
| `log_manager.sh` | 日志管理工具    | 日志查看、清理、统计  |

## 1.2. 核心脚本详解

### 1.2.1. restart.sh - 服务重启脚本

**主要功能**: 一键重启 Django 服务，支持开发和生产环境

```bash
# 基本用法
./restart.sh          # 生产环境（默认）
./restart.sh dev      # 开发环境
./restart.sh prd      # 生产环境
```

**核心特性**:

- 🔄 自动停止现有 Django 进程
- 🚀 启动新的 Django 服务
- 📝 自动日志轮转检查
- ⏰ 设置定时日志轮转任务（每小时）
- 🎯 环境配置自动切换

### 1.2.2. log_rotate.sh - 日志轮转脚本

**主要功能**: 自动管理日志文件大小和数量

```bash
./log_rotate.sh
```

**配置参数**:

- 最大文件大小: **100MB**
- 保留文件数量: **5 个**
- 轮转命名: `django.log.1`, `django.log.2`, ...

**工作流程**:

1. 检查当前日志文件大小
2. 超过 100MB 时自动轮转
3. 删除最旧文件，保留最新 5 个
4. 重命名现有轮转文件

### 1.2.3. log_manager.sh - 日志管理工具

**主要功能**: 综合日志管理，提供多种操作选项

```bash
./log_manager.sh [选项]
```

**可用命令**:

| 命令        | 功能           | 示例                           |
| ----------- | -------------- | ------------------------------ |
| `status`    | 显示日志状态   | `./log_manager.sh status`      |
| `tail`      | 查看最后 50 行 | `./log_manager.sh tail`        |
| `tail -n N` | 查看最后 N 行  | `./log_manager.sh tail -n 100` |
| `rotate`    | 手动轮转       | `./log_manager.sh rotate`      |
| `clean`     | 清理所有日志   | `./log_manager.sh clean`       |
| `stats`     | 显示统计信息   | `./log_manager.sh stats`       |
| `help`      | 显示帮助       | `./log_manager.sh help`        |

## 1.3. 快速开始

### 1.3.1. 首次使用

```bash
# 1. 设置执行权限
chmod +x bin/*.sh

# 2. 启动服务
./bin/restart.sh

# 3. 查看日志状态
./bin/log_manager.sh status
```

### 1.3.2. 日常操作

```bash
# 重启服务
./bin/restart.sh

# 查看实时日志
./bin/log_manager.sh tail

# 手动轮转日志
./bin/log_manager.sh rotate

# 查看日志统计
./bin/log_manager.sh stats
```

## 1.4. 日志文件结构

```
logs/
├── django.log          # 当前日志文件
├── django.log.1        # 轮转日志文件1
├── django.log.2        # 轮转日志文件2
├── django.log.3        # 轮转日志文件3
├── django.log.4        # 轮转日志文件4
├── django.log.5        # 轮转日志文件5
└── log_rotate.log      # 轮转脚本执行日志
```

## 1.5. 环境配置

脚本通过 `config.sh` 文件管理环境配置：

```bash
# 开发环境
DEV_PYTHON_CMD="python3"
DEV_SETTINGS_MODULE="django_base.settings"

# 生产环境
PRD_PYTHON_CMD="python"
PRD_SETTINGS_MODULE="django_base.settings"
```

## 1.6. 定时任务

`restart.sh` 会自动设置定时任务：

```bash
# 每小时检查日志轮转
0 * * * * /path/to/bin/log_rotate.sh >> /path/to/logs/log_rotate.log 2>&1
```

## 1.7. 故障排除

### 1.7.1. 常见问题

| 问题           | 解决方案                   |
| -------------- | -------------------------- |
| 脚本无执行权限 | `chmod +x bin/*.sh`        |
| 定时任务未生效 | `crontab -l` 检查任务      |
| 日志轮转失败   | 查看 `logs/log_rotate.log` |
| 环境变量错误   | 检查 `config.sh` 配置      |

### 1.7.2. 调试命令

```bash
# 检查定时任务
crontab -l

# 查看轮转日志
cat logs/log_rotate.log

# 检查进程状态
ps aux | grep python
```

## 1.8. 自定义配置

如需修改日志轮转参数，编辑 `log_rotate.sh`：

```bash
MAX_SIZE_MB=100  # 最大文件大小（MB）
MAX_FILES=5      # 保留文件数量
```

## 1.9. 注意事项

- ✅ 脚本兼容 macOS 和 Linux
- ✅ 自动检测项目根目录
- ✅ 支持开发和生产环境切换
- ⚠️ `clean` 命令会删除所有日志文件
- ⚠️ 确保 `config.sh` 文件存在且可读
