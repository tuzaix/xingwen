# 星纹 AI 手相项目 - 部署指南

本指南将协助您从零开始部署“星纹 AI 手相”系统，包括后端 API、管理后台以及 H5 用户端。

## 一、 环境要求

- **操作系统**: Linux (推荐 Ubuntu 22.04+) / macOS / Windows
- **Python**: 3.10+
- **Node.js**: 18.0+
- **MySQL**: 8.0+
- **Redis**: 6.0+
- **字体文件**: 确保 `backend/api/app/assets/fonts/` 目录下包含必要的字体文件 (如 OPPOSans)。

---

## 二、 后端部署 (Backend)

### 1. 准备环境
```bash
cd backend/api
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置文件
复制 `.env.example` 为 `.env` 并根据实际环境修改：
```bash
cp .env.example .env
```
重点修改项：
- `DB_DRIVER`: 数据库驱动 (默认 mysql+aiomysql)
- `DB_HOST`: MySQL 地址
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名
- `REDIS_HOST`: Redis 地址
- `AI_API_KEY`: 大模型 API Key (Gemini/OpenAI 等)
- `AI_BASE_URL`: API 代理地址 (如有)

### 3. 初始化项目
我们提供了一个一键初始化脚本，会自动创建数据库、运行迁移并注入初始数据：
```bash
python init_project.py
```
**注意**: 运行前请确保 MySQL 服务已启动且 `DATABASE_URL` 配置正确。

### 4. 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 三、 前端部署 (Frontend)

项目包含两个前端工程：`admin` (管理后台) 和 `h5` (用户端)。

### 1. 管理后台 (Admin)
```bash
cd frontend/admin
cp .env.example .env
npm install
# 开发运行
npm run dev
# 生产构建
npm run build
```

### 2. 用户端 (H5)
```bash
cd frontend/h5
cp .env.example .env
npm install
# 开发运行
npm run dev
# 生产构建
npm run build
```

---

## 四、 Docker 部署 (推荐)

如果您安装了 Docker 和 Docker Compose，可以使用一键部署方案：

```bash
# 在项目根目录运行
docker-compose up -d
```

Docker Compose 会自动启动：
- MySQL 数据库
- Redis 缓存
- Backend API 服务
- Admin 管理后台 (Nginx 驱动)
- H5 用户端 (Nginx 驱动)

---

## 五、 初始账号信息

- **管理后台**: `http://localhost:5173` (具体端口取决于开发环境或 Nginx 配置)
- **默认管理员**: `admin`
- **默认密码**: `admin123`
- **测试卡密**: `XW12345678123456`

---

## 六、 常见问题 (FAQ)

1. **字体显示为方块**: 检查后端 `app/assets/fonts` 是否缺失字体文件，或在 `.env` 中指定正确的路径。
2. **API 404 错误**: 检查前端 `.env` 中的 `VITE_API_BASE_URL` 是否指向了正确的后端地址及端口。
3. **数据库连接失败**: 确保 MySQL 允许远程连接或主机地址正确，且已通过 `init_project.py` 创建了数据库。
