# 1. tools_wangqy_top_backend

tools.wangqy.top 后端

# 2. 版本要求

1. python 版本：`3.9.6`
2. django 版本：`4.2.23`
3. sqlite 版本：`3.8.3`及以上
4. 使`django-admin`命令生效：

```shell
echo 'export PATH="$PATH:/Users/kodyqywang/Library/Python/3.9/bin"' >> ~/.zshrc
source ~/.zshrc  # 重新加载配置
```

4. 启动项目：

```shell
python -m venv .venv
source .venv/bin/activate
django-admin startproject django_base
cd django_base
python manage.py runserver
```

# 3. 生产环境

使用 pyenv

```shell
pyenv install 3.9.6
pyenv virtualenv 3.9.6 tools_wangqy_top_backend
pyenv activate tools_wangqy_top_backend
/root/.pyenv/versions/3.9.6/envs/tools_wangqy_top_backend/bin/python --version
```

# 4. 新建 app

```shell
python manage.py startapp <app name>
```
