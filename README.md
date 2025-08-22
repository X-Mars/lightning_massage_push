# ⚡ 闪电推送 - 企业级消息推送系统

![闪电推送](./frontend/src/assets/lightning.svg)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5.13-brightgreen.svg)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://typescriptlang.org/)

## 功能强大、易于使用的前后端分离消息推送系统

支持企业微信、飞书、钉钉多平台消息推送 | 智能分发 | 模板引擎 | 实时监控

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [API文档](#-api文档) • [生产部署](#-生产环境部署)

---

## 📖 项目简介

闪电推送是一个现代化的企业级消息推送系统，采用前后端分离架构，专为企业内部通知、告警分发、系统集成等场景设计。系统支持多种主流通讯平台的机器人推送，提供灵活的模板系统和智能分发机制。

### 🎯 设计理念

- **简洁高效**: 简单易用的界面设计，快速上手
- **功能强大**: 支持复杂的消息模板和分发规则
- **安全可靠**: 完整的认证授权机制和错误处理
- **易于扩展**: 模块化设计，便于功能扩展和定制

## 🌟 功能特性

### 核心功能

- 🤖 **多平台支持**: 企业微信、飞书、钉钉机器人全支持
- 📝 **智能模板**: 基于Jinja2的强大模板引擎，支持变量、条件、循环等
- 🔄 **高级分发**: 基于规则的智能消息分发系统
- 📊 **实时监控**: 完整的发送日志和数据统计分析
- 🔐 **安全认证**: JWT Token认证，支持用户权限管理
- 🎨 **现代界面**: 基于Element Plus的美观响应式界面

### 高级特性

- 🚀 **Prometheus集成**: 原生支持Prometheus告警数据解析
- 📈 **数据可视化**: ECharts图表展示消息发送趋势
- 🔗 **API接口**: 丰富的REST API，易于第三方系统集成
- 🎛️ **批量操作**: 支持批量配置和管理
- 📱 **响应式设计**: 完美适配PC和移动端
- 🔧 **一键部署**: 提供完整的部署脚本和Docker支持
- 🌍 **多环境支持**: 完整的开发/测试/预发布/生产环境配置体系

## 🏗️ 技术架构

### 系统架构图

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)    │────│  后端 (Django)   │────│  消息推送平台    │
│                 │    │                 │    │                 │
│ • 用户界面      │    │ • REST API      │    │ • 企业微信       │
│ • 数据可视化    │────│ • 认证授权      │────│ • 飞书          │
│ • 响应式设计    │    │ • 消息处理      │    │ • 钉钉          │
│ • 状态管理      │    │ • 模板引擎      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────│  数据库 (SQLite) │
                        │                 │
                        │ • 用户数据      │
                        │ • 消息模板      │
                        │ • 发送日志      │
                        │ • 分发配置      │
                        └─────────────────┘
```

### 技术栈详情

#### 🖥️ 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.5.13 | 渐进式JavaScript框架 |
| TypeScript | 5.8+ | 静态类型检查 |
| Vite | 6.3+ | 现代化构建工具 |
| Element Plus | 2.9+ | UI组件库 |
| ECharts | 5.6+ | 数据可视化 |
| Pinia | 3.0+ | 状态管理 |
| Vue Router | 4.5+ | 路由管理 |
| Axios | 1.9+ | HTTP客户端 |

#### 🔧 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Django | 5.2.1 | Web框架 |
| Django REST Framework | 3.16+ | API框架 |
| Simple JWT | 5.5+ | JWT认证 |
| Jinja2 | 3.1+ | 模板引擎 |
| SQLite | 3.x | 数据库 |
| Requests | 2.32+ | HTTP客户端 |

## 📁 项目结构

```text
message-push-system/
├── 📄 start.sh                    # 一键启动脚本
├── 📄 README.md                   # 项目说明文档
├── 📁 backend/                    # Django后端项目
│   ├── 📄 manage.py               # Django管理脚本
│   ├── 📄 requirements.txt        # Python依赖
│   ├── 📄 db.sqlite3             # SQLite数据库
│   ├── 📁 messagepush/           # 项目配置包
│   │   ├── 📄 settings.py        # Django配置
│   │   ├── 📄 urls.py            # 根URL配置
│   │   └── 📄 wsgi.py            # WSGI配置
│   └── 📁 push/                  # 推送应用
│       ├── 📄 models.py          # 数据模型
│       ├── 📄 views.py           # 视图控制器
│       ├── 📄 serializers.py     # 序列化器
│       ├── 📄 services.py        # 业务逻辑
│       ├── 📄 urls.py            # URL路由
│       ├── 📄 admin.py           # 后台管理
│       ├── 📄 dashboard.py       # 仪表盘API
│       └── 📁 migrations/        # 数据库迁移
└── 📁 frontend/                  # Vue前端项目
    ├── 📄 package.json           # NPM配置
    ├── 📄 vite.config.ts         # Vite配置
    ├── 📄 tsconfig.json          # TypeScript配置
    ├── 📄 index.html             # 入口HTML
    ├── 📄 .env.development       # 开发环境配置
    ├── 📄 .env.test              # 测试环境配置
    ├── 📄 .env.staging           # 预发布环境配置
    ├── 📄 .env.production        # 生产环境配置
    ├── 📄 ENV_CONFIG_GUIDE.md    # 环境配置使用指南
    └── 📁 src/                   # 源代码目录
        ├── 📄 main.ts            # 应用入口
        ├── 📄 App.vue            # 根组件
        ├── 📄 env.d.ts           # 环境变量类型定义
        ├── 📁 api/               # API接口层
        ├── 📁 assets/            # 静态资源
        ├── 📁 components/        # 公共组件
        ├── 📁 router/            # 路由配置
        ├── 📁 stores/            # 状态管理
        ├── 📁 types/             # TypeScript类型
        ├── 📁 utils/             # 工具函数
        │   ├── 📄 envConfig.ts   # 环境配置工具类
        │   └── 📄 apiConfig.ts   # API配置工具类
        └── 📁 views/             # 页面组件
            ├── 📁 template/      # 模板管理
            ├── 📁 robot/         # 机器人管理
            ├── 📁 message/       # 消息管理
            ├── 📁 distribution/  # 分发配置
            └── 📁 prometheus/    # Prometheus集成
```

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **NPM**: 8.0 或更高版本

### ⚡ 一键启动

```bash
# 克隆项目
git clone https://github.com/X-Mars/lightning_massage_push.git
cd lightning_massage_push

# 运行启动脚本
chmod +x start.sh
./start.sh
```

启动脚本会自动完成以下操作：

1. ✅ 创建Python虚拟环境
2. ✅ 安装后端依赖
3. ✅ 执行数据库迁移
4. ✅ 安装前端依赖
5. ✅ 启动后端服务 (<http://localhost:8000>)
6. ✅ 启动前端服务 (<http://localhost:5173>)

### 🔧 手动部署

#### 🏗️ 后端部署

1. 进入后端目录：

```bash
cd message-push-system/backend
```

#### 创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 配置数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 创建管理员账户

```bash
python manage.py createsuperuser
```

#### 启动开发服务器

```bash
python manage.py runserver
```

#### 🎨 前端部署

1. 进入前端目录：

```bash
cd message-push-system/frontend
```

#### 安装项目依赖

```bash
npm install
```

#### 环境配置

项目支持多环境配置，已预置4个环境文件：

- `.env.development` - 开发环境
- `.env.test` - 测试环境
- `.env.staging` - 预发布环境
- `.env.production` - 生产环境

根据需要修改对应环境文件中的配置：

```bash
# 修改开发环境配置
vim .env.development

# 修改生产环境配置
vim .env.production
```

#### 开发模式启动

```bash
# 开发环境（默认）
npm run dev

# 测试环境
npm run dev:test

# 预发布环境
npm run dev:staging
```

#### 生产环境构建

```bash
# 生产构建（默认）
npm run build

# 指定环境构建
npm run build:dev      # 开发构建
npm run build:test     # 测试构建
npm run build:staging  # 预发布构建
npm run build:prod     # 生产构建
```

#### 预览构建结果

```bash
# 预览生产构建
npm run preview

# 预览其他环境构建
npm run preview:test
npm run preview:staging
npm run preview:prod
```

### 🌍 环境配置说明

#### 环境变量配置

每个环境文件支持以下配置项：

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| `VITE_NODE_ENV` | 节点环境 | `development` |
| `VITE_API_BASE_URL` | API基础地址 | `http://localhost:8000` |
| `VITE_APP_TITLE` | 应用标题 | `闪电推送系统` |
| `VITE_DEBUG` | 调试模式 | `true/false` |
| `VITE_LOG_LEVEL` | 日志级别 | `debug/info/warn/error` |
| `VITE_SHOW_ENV_TAG` | 显示环境标识 | `true/false` |
| `VITE_API_TIMEOUT` | API超时时间(ms) | `10000` |

#### 环境特性对比

| 特性 | 开发环境 | 测试环境 | 预发布环境 | 生产环境 |
|------|----------|----------|------------|----------|
| 调试模式 | ✅ | ✅ | ❌ | ❌ |
| 环境标识 | ✅ | ✅ | ✅ | ❌ |
| 开发工具 | ✅ | ✅ | ❌ | ❌ |
| 源码映射 | ✅ | ✅ | ✅ | ❌ |
| 代码压缩 | ❌ | ❌ | ✅ | ✅ |
| 错误上报 | ❌ | ❌ | ✅ | ✅ |

#### 部署建议

- **开发环境**: 使用 `npm run dev` 进行本地开发
- **测试环境**: 使用 `npm run build:test` 构建后部署到测试服务器
- **预发布环境**: 使用 `npm run build:staging` 构建，进行上线前最后验证
- **生产环境**: 使用 `npm run build:prod` 构建，确保性能和安全性最优

## 📚 API文档

### 🔐 认证接口

所有API请求（除了公共推送接口）都需要JWT认证。

#### 获取访问令牌

```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应示例：**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 刷新访问令牌

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

### 🚀 消息推送接口

#### 认证推送接口

```http
POST /api/push/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "template_id": 1,
  "robot_id": 1,
  "content": {
    "title": "系统告警",
    "service": "用户服务",
    "level": "严重",
    "message": "数据库连接失败"
  }
}
```

#### 公共推送接口（无需认证）

```http
POST /api/public/push/{template_id}/{robot_id}/
Content-Type: application/json

{
  "title": "系统通知",
  "content": "系统将于今晚进行维护"
}
```

#### 模板直推接口

```http
POST /api/templates/{template_id}/send/
Content-Type: application/json

{
  "project_name": "电商平台",
  "environment": "生产环境",
  "alert_time": "2025-01-01 12:00:00",
  "description": "支付服务异常"
}
```

### 🤖 机器人管理接口

#### 获取机器人列表

```http
GET /api/robots/
Authorization: Bearer your_access_token
```

#### 创建机器人

```http
POST /api/robots/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "name": "测试机器人",
  "english_name": "test_robot",
  "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
  "robot_type": "wechat",
  "is_default": false
}
```

### 📝 模板管理接口

#### 获取模板列表

```http
GET /api/templates/
Authorization: Bearer your_access_token
```

#### 创建消息模板

```http
POST /api/templates/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "name": "系统告警模板",
  "robot_type": "wechat",
  "content": "## 🚨 系统告警\n**项目**: {{ project_name }}\n**环境**: {{ environment }}\n**时间**: {{ alert_time }}\n**描述**: {{ description }}"
}
```

### 🔄 高级分发接口

#### Prometheus分发推送

```http
POST /api/public/distribution/push/
Content-Type: application/json

{
  "receiver": "webhook",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "instance": "192.168.1.100:9090",
        "project_custom": "电商平台",
        "cluster": "生产集群",
        "severity": "critical"
      },
      "annotations": {
        "summary": "实例宕机告警",
        "description": "实例 192.168.1.100:9090 无法访问"
      }
    }
  ]
}
```

### 📊 仪表盘接口

#### 获取统计数据

```http
GET /api/dashboard/stats/
Authorization: Bearer your_access_token
```

#### 获取图表数据

```http
GET /api/dashboard/charts/?time_range=week
Authorization: Bearer your_access_token
```

## 💡 使用场景

### 🏢 企业内部通知

- **系统维护通知**: 提前通知用户系统维护时间
- **版本发布通知**: 新功能上线或Bug修复通知
- **会议提醒**: 重要会议或培训提醒
- **考勤提醒**: 打卡、请假审批等提醒

### 🚨 监控告警集成

- **服务器监控**: CPU、内存、磁盘使用率告警
- **应用监控**: 服务可用性、响应时间异常
- **业务监控**: 订单量异常、支付失败率过高
- **安全监控**: 异常登录、权限变更等安全事件

### 🔗 第三方系统集成

- **CI/CD流水线**: 构建、测试、部署状态通知
- **工单系统**: 工单创建、处理、完成状态推送
- **CRM系统**: 客户服务、销售机会等业务通知
- **ERP系统**: 库存预警、订单状态等运营通知

### 📈 数据报表推送

- **日报推送**: 每日业务数据汇总
- **周报推送**: 周度运营数据分析
- **异常报告**: 数据异常自动分析和推送
- **定时报表**: 自定义时间的数据报表

## 🎨 模板示例

### 基础文本模板

```jinja2
## 📢 系统通知
**标题**: {{ title }}
**内容**: {{ content }}
**时间**: {{ timestamp }}
```

### 告警模板

```jinja2
## 🚨 {{ severity }} 级告警

**项目**: {{ project_name }}
**环境**: {{ environment }}
**实例**: {{ instance }}
**告警时间**: {{ alert_time }}

### 详细信息
{{ description }}

{% if solution %}
### 解决方案
{{ solution }}
{% endif %}

> 请相关人员及时处理
```

### 业务报表模板

```jinja2
## 📊 {{ report_type }} - {{ date }}

### 核心指标
- **用户访问量**: {{ pv | default('N/A') }}
- **新增用户**: {{ new_users | default('N/A') }}
- **订单数量**: {{ orders | default('N/A') }}
- **成交金额**: ¥{{ revenue | default('0') }}

{% if top_products %}
### 热销商品 TOP5
{% for product in top_products %}
{{ loop.index }}. {{ product.name }} - 销量: {{ product.sales }}
{% endfor %}
{% endif %}

### 数据趋势
{% if trend == 'up' %}
📈 较昨日上升 {{ change_rate }}%
{% elif trend == 'down' %}
📉 较昨日下降 {{ change_rate }}%
{% else %}
➡️ 与昨日持平
{% endif %}
```

## 🔧 配置指南

### 🤖 机器人配置

#### 企业微信机器人

1. 在企业微信群中添加机器人
2. 获取Webhook地址
3. 在系统中创建机器人配置：
   - 类型选择：`企业微信`
   - 粘贴Webhook URL

#### 飞书机器人

1. 在飞书群中添加自定义机器人
2. 获取Webhook地址
3. 在系统中创建机器人配置：
   - 类型选择：`飞书`
   - 粘贴Webhook URL

#### 钉钉机器人

1. 在钉钉群中添加自定义机器人
2. 设置安全设置（关键词或IP白名单）
3. 获取Webhook地址
4. 在系统中创建机器人配置：
   - 类型选择：`钉钉`
   - 粘贴Webhook URL

### 🔄 分发规则配置

#### JSON模式提取规则

用于提取Prometheus等JSON格式数据：

```javascript
// 提取告警实例
alerts[].labels.instance

// 提取项目名称
alerts[].labels.project_custom

// 提取集群信息
alerts[].labels.cluster

// 提取告警级别
alerts[].labels.severity
```

#### 字符串模式提取规则

用于提取普通文本中的信息：

```regex
// 提取IP地址
(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})

// 提取服务名称
service:\s*([^\s,]+)

// 提取时间戳
\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}
```

## 🛡️ 安全配置

### 🔐 认证安全

#### JWT配置

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),    # 访问令牌有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # 刷新令牌有效期
    'ROTATE_REFRESH_TOKENS': True,                 # 自动轮换刷新令牌
    'BLACKLIST_AFTER_ROTATION': True,              # 轮换后加入黑名单
}
```

#### 密码策略

- 最少8位字符
- 包含大小写字母
- 包含数字和特殊字符
- 定期提醒更换密码

### 🔒 访问控制

#### CORS配置

```python
# 生产环境建议指定具体域名
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://subdomain.yourdomain.com",
]

# 开发环境可使用
CORS_ALLOW_ALL_ORIGINS = True
```

#### 接口访问限制

- 认证接口：需要有效Token
- 公共接口：IP白名单控制
- 管理接口：管理员权限验证

### 🔍 审计日志

系统自动记录以下操作：

- 用户登录/登出
- 消息发送记录
- 配置变更操作
- API调用日志
- 错误异常记录

## 🚀 生产环境部署

### 🐳 Docker部署

#### 创建Dockerfile

**后端Dockerfile：**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**前端Dockerfile：**

```dockerfile
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

#### Docker Compose配置

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your_secret_key_here
    volumes:
      - ./backend:/app
      - static_volume:/app/static
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=messagepush
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_volume:
```

### 🌐 Nginx配置

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /app/static/;
    }
}
```

## 🔍 监控与运维

### 📊 系统监控

#### 应用性能监控

- **响应时间监控**: API接口响应时间统计
- **错误率监控**: 请求失败率和错误类型分析
- **吞吐量监控**: 每秒处理请求数(QPS)统计
- **资源监控**: CPU、内存、磁盘使用率

#### 业务指标监控

- **消息发送量**: 实时和历史消息发送统计
- **成功率**: 消息推送成功率统计
- **机器人状态**: 各平台机器人连通性监控
- **用户活跃度**: 用户登录和操作频率分析

### 🚨 告警配置

#### 系统告警

```yaml
# 系统告警规则示例
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05
    duration: 5m
    action: send_notification
    
  - name: slow_response
    condition: avg_response_time > 2s
    duration: 3m
    action: send_notification
    
  - name: service_down
    condition: service_status == "down"
    duration: 1m
    action: send_notification
```

### 📝 日志管理

#### 日志级别配置

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

## 📈 性能优化

### 🚀 后端优化

#### 数据库优化

- **索引优化**: 为查询频繁的字段添加索引
- **查询优化**: 使用select_related和prefetch_related减少数据库查询
- **连接池**: 配置数据库连接池提高并发性能
- **缓存策略**: 使用Redis缓存热点数据

#### API优化

- **分页处理**: 大数据量接口使用分页
- **异步处理**: 耗时操作使用异步任务
- **压缩传输**: 启用Gzip压缩减少传输大小
- **限流控制**: 实现接口访问频率限制

### 💻 前端优化

#### 构建优化

- **代码分割**: 按路由分割代码，实现懒加载
- **Tree Shaking**: 移除未使用的代码
- **资源压缩**: 压缩CSS、JS、图片资源
- **CDN加速**: 静态资源使用CDN加速

#### 运行时优化

- **组件缓存**: 使用keep-alive缓存组件
- **虚拟滚动**: 大列表使用虚拟滚动技术
- **防抖节流**: 搜索等操作使用防抖节流
- **预加载**: 关键资源预加载提升体验

## 🤝 贡献指南

### 📋 开发流程

1. **Fork项目** 到个人仓库
2. **创建特性分支** `git checkout -b feature/amazing-feature`
3. **提交更改** `git commit -m 'Add some amazing feature'`
4. **推送分支** `git push origin feature/amazing-feature`
5. **创建Pull Request**

### 🔧 开发规范

#### 代码规范

- **Python**: 遵循PEP8编码规范
- **JavaScript/TypeScript**: 使用ESLint和Prettier
- **Vue**: 遵循Vue官方风格指南
- **CSS**: 使用BEM命名规范

#### 提交规范

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型：**

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或工具变动

### 🧪 测试指南

#### 后端测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test push

# 生成覆盖率报告
coverage run --source='.' manage.py test
coverage report
```

#### 前端测试

```bash
# 单元测试
npm run test:unit

# 端到端测试
npm run test:e2e

# 测试覆盖率
npm run test:coverage
```

## 🌍 环境配置详解

### 📋 环境文件说明

系统采用基于 Vite 的多环境配置方案，支持以下4个预定义环境：

| 环境 | 文件名 | 用途 | API地址示例 |
|------|--------|------|-------------|
| 开发环境 | `.env.development` | 本地开发调试 | `http://localhost:8000` |
| 测试环境 | `.env.test` | 功能测试验证 | `http://test-api.example.com` |
| 预发布环境 | `.env.staging` | 上线前验证 | `https://staging-api.example.com` |
| 生产环境 | `.env.production` | 正式生产环境 | `https://api.example.com` |

### ⚙️ 环境变量说明

#### 核心配置项

```bash
# 节点环境
VITE_NODE_ENV=development

# API基础地址（必须配置）
VITE_API_BASE_URL=http://localhost:8000

# 应用信息
VITE_APP_TITLE=闪电推送系统
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_DEBUG=true                    # 调试模式
VITE_SHOW_ENV_TAG=true            # 显示环境标识
VITE_DEV_TOOLS=true               # 开发工具
```

#### 网络配置

```bash
# API配置
VITE_API_TIMEOUT=10000            # API超时时间(ms)
VITE_WS_BASE_URL=ws://localhost:8000  # WebSocket地址

# CDN配置
VITE_CDN_URL=https://cdn.example.com
```

#### 监控与分析

```bash
# 日志配置
VITE_LOG_LEVEL=debug              # debug|info|warn|error

# 监控配置
VITE_ENABLE_PERFORMANCE=true      # 性能监控
VITE_ENABLE_ERROR_REPORTING=true  # 错误上报
VITE_SENTRY_DSN=                  # Sentry DSN

# 统计分析
VITE_ENABLE_ANALYTICS=true        # 统计分析
```

### 🚀 使用示例

#### 代码中使用环境变量

```typescript
// 直接使用
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const isDebug = import.meta.env.VITE_DEBUG === 'true';

// 使用环境配置工具类
import { EnvConfig } from '@/utils/envConfig';

console.log(EnvConfig.apiBaseUrl);      // API地址
console.log(EnvConfig.isProduction);    // 是否生产环境
console.log(EnvConfig.appVersion);      // 应用版本

// 环境判断
if (EnvConfig.isDevelopment) {
  // 开发环境特有逻辑
}
```

#### 部署脚本示例

```bash
#!/bin/bash
# 部署脚本示例

# 测试环境部署
echo "构建测试环境..."
npm run build:test
echo "部署到测试服务器..."
rsync -av dist/ user@test-server:/var/www/html/

# 生产环境部署
echo "构建生产环境..."
npm run build:prod
echo "部署到生产服务器..."
rsync -av dist/ user@prod-server:/var/www/html/
```

### 🔧 自定义环境

如需新增环境，按以下步骤操作：

1. **创建环境文件**：`touch .env.{环境名}`
2. **配置package.json脚本**：

   ```json
   {
     "scripts": {
       "dev:custom": "vite --mode custom",
       "build:custom": "vue-tsc -b && vite build --mode custom"
     }
   }
   ```

3. **更新环境工具类**：在 `EnvConfig` 中添加环境判断
4. **配置部署流程**：更新CI/CD脚本

### 📝 配置文件参考

详细的环境配置说明请参考：[ENV_CONFIG_GUIDE.md](frontend/ENV_CONFIG_GUIDE.md)

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议发布。

## 🙏 致谢

感谢以下开源项目和技术：

- [Django](https://djangoproject.com/) - 强大的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - 优秀的Vue 3组件库
- [ECharts](https://echarts.apache.org/) - 强大的数据可视化库
- [Jinja2](https://jinja.palletsprojects.com/) - 灵活的模板引擎

## 📞 联系我们

- **作者**: X-Mars
- **项目地址**: [GitHub](https://github.com/X-Mars/lightning_massage_push)
- **问题反馈**: [Issues](https://github.com/X-Mars/lightning_massage_push/issues)
- **功能建议**: [Discussions](https://github.com/X-Mars/lightning_massage_push/discussions)

## 🔗 相关链接

<!-- - [在线文档](https://your-docs-site.com)
- [演示站点](https://your-demo-site.com)
- [更新日志](CHANGELOG.md)
- [开发路线图](ROADMAP.md) -->

---

**⭐ 如果这个项目对你有帮助，请给它一个星标！**

[![Star History Chart](https://api.star-history.com/svg?repos=X-Mars/lightning_massage_push&type=Date)](https://star-history.com/#X-Mars/lightning_massage_push&Date)
