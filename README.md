# 消息推送系统说明文档

这是一个前后端分离的消息推送系统，支持将信息推送到企业微信、飞书和钉钉机器人。

## 项目结构

```
message-push-system/
├── start.sh         # 一键启动脚本
├── README.md        # 说明文档
├── backend/         # Django 后端
│   ├── manage.py
│   ├── requirements.txt
│   ├── messagepush/ # 项目配置
│   └── push/        # 推送应用
└── frontend/        # Vue 前端
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/         # 源代码
        ├── api/     # API调用
        ├── assets/  # 静态资源
        ├── components/ # 组件
        ├── router/  # 路由
        ├── stores/  # 状态管理
        ├── types/   # 类型定义
        └── views/   # 页面视图
```

## 功能特性

- 支持将消息推送到企业微信、飞书、钉钉机器人
- 支持通过Jinja2模板格式化信息
- 提供API接口，接收其他系统推送请求
- 完整的用户认证和授权系统
- 美观的UI界面，支持数据可视化
- 详细的消息发送日志记录

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Element Plus
- Axios
- ECharts
- Vue Router
- Pinia

### 后端

- Django 5
- Django REST Framework
- Simple JWT认证
- Jinja2模板引擎

## 部署指南

### 后端部署

1. 进入后端目录：

```bash
cd message-push-system/backend
```

2. 安装依赖：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. 执行数据库迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建管理员用户：

```bash
python manage.py createsuperuser
```

5. 运行开发服务器：

```bash
python manage.py runserver
```

### 前端部署

1. 进入前端目录：

```bash
cd message-push-system/frontend
```

2. 安装依赖：

```bash
npm install
```

3. 开发模式运行：

```bash
npm run dev
```

4. 构建生产版本：

```bash
npm run build
```

## API文档

### 认证

所有API请求（除了公共推送接口）都需要JWT认证。

**获取Token**

```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**刷新Token**

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

### 消息推送

**向机器人发送消息（认证后）**

```http
POST /api/push/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "template_id": 1,
  "robot_id": 1,
  "content": {
    "title": "标题",
    "content": "内容"
  }
}
```

**公共推送接口（无需认证）**

```http
POST /api/public/push/{template_id}/{robot_id}/
Content-Type: application/json

{
  "title": "标题",
  "content": "内容"
}
```

## 注意事项

1. 生产环境部署时，请修改Django的SECRET_KEY和设置DEBUG=False
2. 根据需要配置CORS设置，限制允许访问的源
3. 为保证安全，建议使用HTTPS协议
4. 可以通过Nginx反向代理前后端服务
