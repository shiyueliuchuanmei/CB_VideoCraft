# VideoCraft 🎬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vue 3](https://img.shields.io/badge/Vue-3.4+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)

> 电商视频智能创作平台 - 基于火山引擎豆包大模型的 AI 视频/图片生成工具
>
> 由 [广州十月六传媒有限公司](mailto:McrobbieStruzik518@gmail.com) 开发维护

![VideoCraft Screenshot](./screenshots/dashboard.png)

## ✨ 功能特性

### 🎥 视频生成
- **文生视频**: 输入文字描述，AI 自动生成视频
- **图生视频**: 上传图片作为首帧，生成动态视频
- **多模态输入**: 支持文字 + 图片 + 视频 + 音频组合创作
- **参数调节**: 分辨率(480p/720p/1080p)、时长(5-10秒)、画面比例(9:16/16:9/1:1)

### 🖼️ 图片生成
- **文生图**: 根据描述生成高质量商品图
- **多风格支持**: 支持多种视觉风格和场景
- **批量生成**: 一次可生成多张图片供选择

### 📊 任务管理
- **实时状态**: 查看任务进度(pending/processing/completed/failed)
- **历史记录**: 完整的生成历史，支持搜索和筛选
- **批量操作**: 支持批量下载、删除任务
- **视频预览**: 在线预览生成的视频（支持跨域处理）

### 🔐 用户系统
- **JWT 认证**: 安全的登录机制
- **个人设置**: 自定义默认参数和偏好
- **使用统计**: 查看生成任务统计数据

## 🏗️ 技术架构

### 前端 (Frontend)
```
Vue 3 + Vite + Ant Design Vue + Pinia
```
- **Vue 3**: Composition API，响应式开发
- **Vite**: 极速构建工具
- **Ant Design Vue**: 企业级 UI 组件库
- **Pinia**: 状态管理
- **Axios**: HTTP 客户端

### 后端 (Backend)
```
FastAPI + SQLAlchemy + SQLite + Uvicorn
```
- **FastAPI**: 高性能异步 Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **SQLite**: 轻量级数据库
- **Pydantic**: 数据验证
- **火山引擎 API**: 豆包大模型接入

### 项目结构
```
video-craft/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── components/      # 公共组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── views/           # 页面视图
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── models.py        # 数据模型
│   │   └── database.py      # 数据库配置
│   ├── main.py              # 入口文件
│   └── requirements.txt
│
└── README.md
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- 火山引擎 API Key

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/video-craft.git
cd video-craft
```

### 2. 后端配置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate
# 或 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的火山引擎 API Key
```

**`.env` 配置示例:**
```env
# 应用配置
APP_NAME=VideoCraft
DEBUG=true
SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./videocraft.db

# 火山引擎 API
DOUBAO_API_KEY=your-doubao-api-key-here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:5174"]
```

```bash
# 启动后端服务
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在: http://localhost:8000
API 文档: http://localhost:8000/docs

### 3. 前端配置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在: http://localhost:5173

### 4. 开始使用

1. 打开浏览器访问 http://localhost:5173
2. 注册账号或登录
3. 进入"视频生成"或"图片生成"页面
4. 输入提示词，点击"开始生成"
5. 在"历史记录"页面查看生成结果

## 📖 使用指南

### 视频生成示例

**文生视频:**
1. 选择"文生视频"模式
2. 输入提示词: "一只可爱的猫咪在草地上玩耍，阳光明媚"
3. 选择分辨率: 720p
4. 选择时长: 5秒
5. 点击"开始生成"

**图生视频:**
1. 选择"图生视频"模式
2. 上传首帧图片
3. 输入提示词描述视频内容
4. 点击"开始生成"

### 提示词技巧

- **清晰具体**: 描述主体、动作、场景、光线
- **风格关键词**: "电影感"、"产品展示"、"广告风格"
- **避免**: 过于复杂的场景、多主体动作

**示例:**
```
高端化妆品产品展示，白色简约背景，柔和光线，
镜头缓慢推进，展示产品细节，专业广告风格
```

## 🔧 开发计划

### 已完成功能 ✅
- [x] 用户注册/登录
- [x] 视频生成（文生视频、图生视频）
- [x] 图片生成
- [x] 任务管理（创建、查询、取消、删除）
- [x] 历史记录页面
- [x] 视频在线预览
- [x] 前后端联调

### 进行中 🚧
- [ ] 视频后端代理（解决跨域播放问题）
- [ ] 真实视频生成接入火山引擎
- [ ] 图片生成优化

### 待开发 📋
- [ ] 架构重构（分层设计）
- [ ] 单元测试
- [ ] Docker 部署
- [ ] 云端存储集成（OSS/COS）
- [ ] 批量任务处理
- [ ] 模板系统
- [ ] 团队协作功能

## 🏛️ 架构设计

### 当前架构
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │──────▶│   Backend   │──────▶│   Doubao    │
│  (Vue 3)    │◀──────│  (FastAPI)  │◀──────│   API       │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │   SQLite    │
                      └─────────────┘
```

### 目标架构
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Views     │──────▶│   API Layer │──────▶│  Services   │
│ Components  │      │   (Routers) │      │  (Business) │
│ Composables │      └─────────────┘      └──────┬──────┘
└─────────────┘                                  │
                                                 ▼
                                          ┌─────────────┐
                                          │ Repositories│
                                          │   (Data)    │
                                          └──────┬──────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    ▼                            ▼                            ▼
              ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
              │   SQLite    │            │  Doubao API │            │   OSS/COS   │
              └─────────────┘            └─────────────┘            └─────────────┘
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证

## 🙏 致谢

- [火山引擎](https://www.volcengine.com/) - 提供豆包大模型 API
- [FastAPI](https://fastapi.tiangolo.com/) - 优秀的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Ant Design Vue](https://antdv.com/) - 企业级 UI 组件库

## 📞 联系我们

- **公司**: 广州十月六传媒有限公司
- **项目主页**: https://github.com/shiyueliuchuanmei/video-craft
- **Issue 反馈**: https://github.com/shiyueliuchuanmei/video-craft/issues
- **邮箱**: [McrobbieStruzik518@gmail.com](mailto:McrobbieStruzik518@gmail.com)

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！
