# VideoCraft 架构设计

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Vue 3     │  │ Ant Design  │  │      Pinia          │  │
│  │  (Composition│  │    Vue      │  │    (状态管理)        │  │
│  │    API)     │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        后端层 (Backend)                       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    FastAPI (Python)                      ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  ││
│  │  │ 认证模块  │  │ 用户模块  │  │ 图片模块  │  │视频模块 │  ││
│  │  │  (JWT)   │  │          │  │          │  │        │  ││
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │                   业务服务层 (Services)                  ││
│  │  ┌───────────────────────────────────────────────────┐  ││
│  │  │           豆包 API 服务 (Doubao Service)           │  ││
│  │  │  ┌──────────────┐  ┌──────────────────────────┐  │  ││
│  │  │  │ Seedream     │  │ Seedance                 │  │  ││
│  │  │  │ (图片生成)    │  │ (视频生成)                │  │  ││
│  │  │  └──────────────┘  └──────────────────────────┘  │  ││
│  │  └───────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQL / Redis
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        数据层 (Data)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   SQLite     │  │    Redis     │  │   Local/OSS      │   │
│  │  (主数据库)   │  │  (缓存/队列)  │  │   (文件存储)      │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

### 前端
- **框架**: Vue 3.4+ (Composition API)
- **UI 组件库**: Ant Design Vue 4.x
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **构建工具**: Vite 5
- **样式**: Less + CSS Variables

### 后端
- **框架**: FastAPI 0.109+
- **数据库**: SQLAlchemy 2.0 + SQLite (开发) / PostgreSQL (生产)
- **缓存**: Redis
- **任务队列**: Celery + Redis
- **认证**: JWT (python-jose) + bcrypt
- **HTTP 客户端**: httpx

### AI 服务
- **图片生成**: 豆包 Seedream
- **视频生成**: 豆包 Seedance
- **API 格式**: 兼容 OpenAI API

## 数据模型

### 用户 (User)
```python
{
    id: int,
    email: str,
    name: str,
    avatar: str,
    is_active: bool,
    doubao_api_key: str,      # 豆包 API Key
    storage_type: str,        # 存储类型
    created_at: datetime,
    updated_at: datetime,
}
```

### 任务 (Task)
```python
{
    id: int,
    task_id: str,             # 唯一任务ID
    task_type: str,           # image / video
    status: str,              # pending / processing / completed / failed
    model: str,               # 模型名称
    prompt: str,              # 提示词
    negative_prompt: str,     # 反向提示词
    mode: str,                # 生成模式
    ratio: str,               # 比例
    resolution: str,          # 分辨率
    duration: int,            # 视频时长
    num: int,                 # 生成数量
    output_urls: List[str],   # 输出URL列表
    user_id: int,             # 关联用户
    created_at: datetime,
    completed_at: datetime,
}
```

## API 设计

### RESTful API 规范

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 获取当前用户 |
| GET | /api/users/me | 获取用户信息 |
| PUT | /api/users/me | 更新用户信息 |
| GET | /api/images/models | 获取图片模型列表 |
| POST | /api/images/generations | 创建图片生成任务 |
| GET | /api/images/generations | 获取图片任务列表 |
| GET | /api/images/generations/{id} | 查询图片任务 |
| GET | /api/videos/models | 获取视频模型列表 |
| POST | /api/videos/generations | 创建视频生成任务 |
| GET | /api/videos/generations | 获取视频任务列表 |
| GET | /api/videos/generations/{id} | 查询视频任务 |

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

## 文件存储

### 本地存储
```
uploads/
├── 2026/
│   ├── 04/
│   │   ├── 08/
│   │   │   ├── image_xxx.png
│   │   │   └── video_xxx.mp4
```

### 阿里云 OSS（可选）
- Bucket: videocraft-uploads
- 路径: `{user_id}/{date}/{filename}`

## 安全设计

1. **认证**: JWT Token，有效期 7 天
2. **密码**: bcrypt 加密存储
3. **API Key**: 用户级配置，不共享
4. **CORS**: 白名单限制
5. **文件上传**: 类型和大小限制

## 扩展性设计

1. **模型扩展**: 通过配置文件添加新模型
2. **存储扩展**: 支持本地/OSS/其他云存储
3. **任务队列**: Celery 支持分布式部署
4. **数据库**: SQLAlchemy 支持多种数据库

## 部署架构

### 开发环境
```
本地电脑
├── 前端 (npm run dev) → http://localhost:5173
├── 后端 (uvicorn) → http://localhost:8000
└── Redis → localhost:6379
```

### 生产环境
```
服务器集群
├── Nginx (反向代理 + 静态文件)
├── 前端 (构建后部署)
├── 后端 (Gunicorn + Uvicorn)
├── Redis (缓存 + 队列)
└── 数据库 (PostgreSQL)
```
