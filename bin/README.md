# Django 管理工具

本目录包含了用于管理 Django 项目的脚本工具。

## 脚本文件

### 1. `restart.sh` - 服务重启脚本

**功能**: 重启 Django 服务并自动设置日志轮转
**用法**: `./restart.sh`

**特性**:

- 自动停止现有 Django 进程
- 在启动前执行日志轮转检查
- 启动新的 Django 服务
- 自动设置定时日志轮转任务（每小时执行）
- 显示详细的日志管理信息

### 2. `log_rotate.sh` - 日志轮转脚本

**功能**: 自动轮转 Django 日志文件
**用法**: `./log_rotate.sh`

**配置**:

- 最大文件大小: 100MB
- 保留文件数量: 5 个
- 轮转文件命名: `django.log.1`, `django.log.2`, ...

**工作原理**:

1. 检查当前日志文件大小
2. 如果超过 100MB，执行轮转
3. 删除最旧的日志文件
4. 重命名现有轮转文件
5. 创建新的日志文件

### 3. `log_manager.sh` - 日志管理工具

**功能**: 综合日志管理工具
**用法**: `./log_manager.sh [选项]`

**可用选项**:

- `status` - 显示日志状态信息
- `tail` - 查看最后 50 行日志
- `tail -n N` - 查看最后 N 行日志
- `rotate` - 手动执行日志轮转
- `clean` - 清理所有日志文件
- `stats` - 显示日志统计信息
- `help` - 显示帮助信息

## 使用示例

### 重启服务并设置日志轮转

```bash
./restart.sh
```

### 查看日志状态

```bash
./log_manager.sh status
```

### 实时查看日志

```bash
./log_manager.sh tail
./log_manager.sh tail -n 100
```

### 手动执行日志轮转

```bash
./log_manager.sh rotate
```

### 查看日志统计

```bash
./log_manager.sh stats
```

### 清理所有日志

```bash
./log_manager.sh clean
```

## 日志文件结构

```
$PROJECT_DIR/logs/
├── django.log          # 当前日志文件
├── django.log.1        # 轮转日志文件1
├── django.log.2        # 轮转日志文件2
├── django.log.3        # 轮转日志文件3
├── django.log.4        # 轮转日志文件4
├── django.log.5        # 轮转日志文件5
└── log_rotate.log      # 日志轮转脚本的执行日志
```

## 定时任务

重启脚本会自动设置定时任务，每小时检查一次日志文件大小：

```bash
0 * * * * /path/to/bin/log_rotate.sh >> /path/to/logs/log_rotate.log 2>&1
```

## 注意事项

1. **权限**: 确保脚本有执行权限 (`chmod +x *.sh`)
2. **路径**: 脚本会自动检测项目根目录，无需手动配置路径
3. **定时任务**: 重启脚本会自动设置 crontab 任务，无需手动配置
4. **日志清理**: 使用 `clean` 选项时要小心，会删除所有日志文件
5. **兼容性**: 脚本兼容 macOS 和 Linux 系统

## 故障排除

### 定时任务未生效

检查 crontab 是否正确设置：

```bash
crontab -l
```

### 日志轮转失败

检查日志轮转脚本的执行日志：

```bash
cat $PROJECT_DIR/logs/log_rotate.log
```

### 权限问题

确保脚本有执行权限：

```bash
chmod +x bin/*.sh
```

## 自定义配置

如需修改日志轮转配置，编辑 `log_rotate.sh` 文件中的以下变量：

```bash
MAX_SIZE_MB=100  # 最大文件大小（MB）
MAX_FILES=5      # 保留的日志文件数量
```

# 脚本使用说明

## restart.sh - Django服务重启脚本

### 功能特性

- 支持开发环境和生产环境的区分
- 自动日志轮转管理
- 定时任务设置
- 进程管理

### 使用方法

#### 基本用法

```bash
# 生产环境启动（默认）
./bin/restart.sh

# 或者明确指定生产环境
./bin/restart.sh prd

# 开发环境启动
./bin/restart.sh dev
```

#### 参数说明

- `dev` - 开发环境
  - 使用 `python3` 命令
  - 适用于开发调试
  
- `prd` - 生产环境（默认）
  - 使用 `python` 命令
  - 适用于生产部署

### 环境配置

环境配置在 `bin/config.sh` 文件中管理：

```bash
# 开发环境配置
DEV_PYTHON_CMD="python3"
DEV_SETTINGS_MODULE="src.settings"

# 生产环境配置
PRD_PYTHON_CMD="python"
PRD_SETTINGS_MODULE="src.settings"
```

### 功能说明

1. **进程管理**
   - 自动停止现有的Django服务
   - 启动新的Django服务

2. **日志管理**
   - 自动创建日志目录
   - 日志文件：`logs/django.log`
   - 自动日志轮转（最大100MB，保留5个文件）

3. **定时任务**
   - 自动设置每小时检查日志轮转的crontab任务
   - 避免重复设置

4. **环境变量**
   - 自动设置 `DJANGO_SETTINGS_MODULE` 环境变量
   - 根据环境使用不同的Python可执行命令

### 输出信息

脚本运行时会显示：
- 当前使用的环境配置
- 服务启动状态
- 日志管理信息
- Python命令和Django设置模块

### 注意事项

1. 确保脚本有执行权限
2. 确保配置文件 `config.sh` 存在且可读
3. 生产环境建议使用虚拟环境
4. 日志文件会保存在项目根目录的 `logs` 文件夹中
