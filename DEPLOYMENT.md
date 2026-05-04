# 星纹 AI 手相项目 - 生产环境部署指南 (2026版)

本指南总结了“星纹 AI 手相”系统在 Ubuntu 环境下使用 Gunicorn + Nginx 部署的完整流程，并包含了针对部署过程中遇到的兼容性、路径及网络问题的解决方案。

---

## 一、 环境准备

- **操作系统**: Ubuntu 22.04+ (推荐)
- **Python**: 3.12+ (需安装 `python3-venv`)
- **Node.js**: 18.0+ (需安装 `npm`)
- **MySQL**: 8.0+ (需支持 `utf8mb4`)
- **Redis**: 6.0+

---

## 二、 数据库初始化 (MySQL)

在部署前，请执行以下 SQL 脚本创建数据库及专用用户：

```sql
-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS xingwen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 创建专用用户
CREATE USER 'xingwen'@'%' IDENTIFIED BY 'Xingwen_2026';

-- 3. 授予权限
GRANT ALL PRIVILEGES ON xingwen.* TO 'xingwen'@'%';

-- 4. 刷新权限
FLUSH PRIVILEGES;
```

---

## 三、 后端部署 (Backend)

### 1. 目录结构与环境
假设项目代码位于 `/var/www/xingwen`，虚拟环境位于 `/var/www/zhangjing/backend/venv`。

```bash
cd /var/www/xingwen/backend/api
# 创建并激活虚拟环境 (如已存在请跳过)
python3 -m venv /var/www/zhangjing/backend/venv
source /var/www/zhangjing/backend/venv/bin/activate

# 强制安装所有依赖（包含兼容性补丁所需的库）
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 配置文件 (.env)
复制并修改后端配置：
```bash
cp .env.example .env
```
**关键配置项**:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: 填入上述 SQL 设置的信息。
- `SECRET_KEY`: 生成一个随机长字符串。
- `VITE_API_BASE_URL`: 设置为 `/api/v1` (前端相对路径)。

### 3. 初始化数据
```bash
python init_project.py
```

### 4. Systemd 服务配置
创建 `/etc/systemd/system/xingwen-api.service`:
```ini
[Unit]
Description=Xingwen AI API Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/xingwen/backend/api
Environment="PATH=/var/www/zhangjing/backend/venv/bin"
# 使用 Gunicorn 配合 UvicornWorker，开启 4 个工作进程，监听 8641 端口
ExecStart=/var/www/zhangjing/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8641

[Install]
WantedBy=multi-user.target
```
启动服务：`systemctl enable --now xingwen-api`

---

## 四、 前端部署 (Frontend)

### 1. 环境变量配置
**注意**: 在生产环境下，必须使用相对路径。
- **H5 端** (`frontend/h5/.env`): `VITE_API_BASE_URL=/api/v1`
- **管理后台** (`frontend/admin/.env`): `VITE_API_BASE_URL=/api/v1`

### 2. 编译构建
```bash
# H5 端
cd /var/www/xingwen/frontend/h5
npm install && npm run build

# 管理后台 (已配置 base: '/admin/')
cd /var/www/xingwen/frontend/admin
npm install && npm run build
```

---

## 五、 Nginx 配置 (核心)

创建 `/etc/nginx/sites-available/xingwen`:

```nginx
server {
    listen 80;
    server_name yourdomain.com; # 替换为实际域名

    # 1. H5 用户端 (根目录)
    location / {
        root /var/www/xingwen/frontend/h5/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 专门防止 index.html 递归重定向
    location = /index.html {
        root /var/www/xingwen/frontend/h5/dist;
    }

    # 2. Admin 管理后台 (子目录 /admin)
    # 注意：需在 vite.config.ts 中配置 base: '/admin/'
    location /admin {
        alias /var/www/xingwen/frontend/admin/dist/;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # 3. 静态上传资源 (手相图片)
    location /uploads {
        alias /var/www/xingwen/backend/api/uploads;
        expires 30d;
        add_header Cache-Control "public";
    }

    # 4. 后端 API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8641;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
应用配置：`nginx -t && systemctl restart nginx`

---

## 六、 部署常见问题排查 (FAQ)

### 1. 登录/密码报错: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- **原因**: `passlib` 与新版 `bcrypt` 不兼容。
- **解决**: 已在 `app/core/security.py` 中通过 Monkeypatch 修复。请确保安装了 `bcrypt==4.0.1`。

### 2. 访问空白页/MIME 类型错误
- **报错**: `Expected a JavaScript module script but the server responded with a MIME type of "text/html"`.
- **解决**: 管理后台必须配置 `base: '/admin/'`，且 Nginx 的 `alias` 路径末尾必须带 `/`。

### 3. Nginx 500 错误 (Internal Redirection Cycle)
- **原因**: `root` 路径配置错误，导致 Nginx 找不到 `index.html`。
- **解决**: 确认 `root` 路径指向包含 `index.html` 的 `dist` 目录，并赋予 `www-data` 访问权限：`chown -R www-data:www-data /var/www/xingwen`。

### 4. 后端报错: `ModuleNotFoundError: No module named 'jwt'` 或 `'aiomysql'`
- **原因**: 虚拟环境未正确安装依赖。
- **解决**: 使用全路径 pip 安装：`/path/to/venv/bin/pip install -r requirements.txt`。

### 5. 前端编译警告: `Some chunks are larger than 500 kB`
- **解决**: 已在 `vite.config.ts` 中配置 `manualChunks` 进行代码分割，将 `element-plus` 等大库独立打包。
