# 环境配置使用指南

## 📁 环境文件说明

项目中已创建了 4 个环境配置文件，分别对应不同的部署环境：

### 1. `.env.development` - 开发环境
- **用途**: 本地开发时使用
- **API地址**: `http://localhost:8000`
- **特点**: 启用调试模式、开发工具、详细日志

### 2. `.env.test` - 测试环境
- **用途**: 测试服务器部署
- **API地址**: `http://test-api.example.com`
- **特点**: 启用调试、测试模式、较长的API超时

### 3. `.env.staging` - 预发布环境
- **用途**: 预发布服务器，正式发布前的最后验证
- **API地址**: `https://staging-api.example.com`
- **特点**: 接近生产环境配置，但保留环境标识

### 4. `.env.production` - 生产环境
- **用途**: 正式生产环境
- **API地址**: `https://api.example.com`
- **特点**: 性能优化、错误上报、分析统计

## 🚀 使用方法

### 开发运行
```bash
# 开发环境 (默认)
npm run dev

# 测试环境
npm run dev:test

# 预发布环境  
npm run dev:staging
```

### 构建部署
```bash
# 生产构建 (默认)
npm run build

# 开发构建
npm run build:dev

# 测试构建
npm run build:test

# 预发布构建
npm run build:staging

# 生产构建
npm run build:prod
```

### 预览构建结果
```bash
# 预览生产构建
npm run preview

# 预览测试构建
npm run preview:test

# 预览预发布构建
npm run preview:staging
```

## 🔧 环境变量说明

### 基础配置
- `VITE_NODE_ENV`: 节点环境 (development/test/staging/production)
- `VITE_API_BASE_URL`: API 基础地址
- `VITE_APP_TITLE`: 应用标题
- `VITE_APP_VERSION`: 应用版本

### 功能开关
- `VITE_DEBUG`: 调试模式 (true/false)
- `VITE_USE_MOCK`: 是否使用 Mock 数据
- `VITE_SHOW_ENV_TAG`: 是否显示环境标签
- `VITE_DEV_TOOLS`: 是否启用开发工具

### 网络配置
- `VITE_API_TIMEOUT`: API 超时时间 (毫秒)
- `VITE_WS_BASE_URL`: WebSocket 地址
- `VITE_CDN_URL`: CDN 地址

### 其他配置
- `VITE_LOG_LEVEL`: 日志级别 (debug/info/warn/error)
- `VITE_UPLOAD_SIZE_LIMIT`: 文件上传大小限制 (MB)
- `VITE_ENABLE_PERFORMANCE`: 性能监控
- `VITE_ENABLE_ERROR_REPORTING`: 错误上报

## 💡 代码中使用环境变量

### 1. 直接使用
```typescript
// 获取 API 地址
const apiUrl = import.meta.env.VITE_API_BASE_URL;

// 判断是否为生产环境
const isProduction = import.meta.env.VITE_NODE_ENV === 'production';
```

### 2. 使用 EnvConfig 工具类
```typescript
import { EnvConfig } from '@/utils/envConfig';

// 获取环境信息
console.log(EnvConfig.apiBaseUrl);
console.log(EnvConfig.isProduction);
console.log(EnvConfig.appVersion);

// 环境判断
if (EnvConfig.isDevelopment) {
  // 开发环境特有逻辑
}

// 打印环境信息
EnvConfig.printEnvInfo();
```

## 🎯 部署配置

### 开发环境部署
```bash
npm run build:dev
# 部署到开发服务器
```

### 测试环境部署
```bash
npm run build:test
# 部署到测试服务器
```

### 预发布环境部署
```bash
npm run build:staging
# 部署到预发布服务器
```

### 生产环境部署
```bash
npm run build:prod
# 部署到生产服务器
```

## 🔍 环境识别

1. **环境标签**: 非生产环境会在页面右上角显示环境标识
2. **控制台信息**: 开发和测试环境会在控制台打印环境信息
3. **页面标题**: 不同环境的页面标题会包含环境标识

## ⚠️ 注意事项

1. **API 地址**: 请根据实际情况修改各环境的 API 地址
2. **密钥配置**: 生产环境的敏感信息（如 Sentry DSN）需要在部署时设置
3. **缓存清理**: 切换环境后建议清理浏览器缓存
4. **TypeScript**: 所有环境变量都有完整的类型定义

## 🛠️ 自定义环境

如需添加新的环境，请：

1. 创建对应的 `.env.{环境名}` 文件
2. 在 `package.json` 中添加对应的脚本
3. 在 `EnvConfig` 中添加环境判断逻辑
4. 在 `EnvTag` 组件中添加样式配置
