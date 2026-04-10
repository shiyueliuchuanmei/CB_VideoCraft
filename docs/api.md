# VideoCraft API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 认证

### 注册
```http
POST /auth/register
Content-Type: application/json

{
    "name": "用户名",
    "email": "user@example.com",
    "password": "password123"
}
```

**响应**:
```json
{
    "code": 200,
    "message": "注册成功"
}
```

### 登录
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "用户名",
            "avatar": ""
        }
    }
}
```

### 获取当前用户
```http
GET /auth/me
Authorization: Bearer {token}
```

## 图片生成

### 获取模型列表
```http
GET /images/models
```

**响应**:
```json
{
    "code": 200,
    "data": [
        {
            "id": "seedream-2.0",
            "name": "Seedream 2.0",
            "description": "豆包图片生成模型",
            "supported_ratios": ["1:1", "9:16", "16:9"],
            "supported_resolutions": ["512", "1024", "2048"]
        }
    ]
}
```

### 创建生成任务
```http
POST /images/generations
Authorization: Bearer {token}
Content-Type: application/json

{
    "model": "seedream-2.0",
    "prompt": "一款白色无线耳机，极简风格，产品摄影",
    "negative_prompt": "模糊，低质量",
    "mode": "text2image",
    "ratio": "1:1",
    "resolution": "1024",
    "num": 1
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "task_id": "img_a1b2c3d4e5f67890",
        "status": "pending",
        "message": "图片生成任务已创建"
    }
}
```

### 查询任务状态
```http
GET /images/generations/{task_id}
Authorization: Bearer {token}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "task_id": "img_a1b2c3d4e5f67890",
        "status": "completed",
        "progress": 100,
        "output_urls": [
            "https://example.com/output/1.png"
        ],
        "created_at": "2026-04-08T10:00:00Z",
        "completed_at": "2026-04-08T10:00:30Z"
    }
}
```

### 获取任务列表
```http
GET /images/generations?page=1&page_size=10&status=completed
Authorization: Bearer {token}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 10
    }
}
```

## 视频生成

### 获取模型列表
```http
GET /videos/models
```

**响应**:
```json
{
    "code": 200,
    "data": [
        {
            "id": "seedance-2.0",
            "name": "Seedance 2.0",
            "description": "豆包视频生成模型",
            "supported_ratios": ["9:16", "16:9", "1:1"],
            "supported_resolutions": ["480p", "720p", "1080p"],
            "max_duration": 10
        }
    ]
}
```

### 创建生成任务
```http
POST /videos/generations
Authorization: Bearer {token}
Content-Type: application/json

{
    "model": "seedance-2.0",
    "prompt": "智能手表在手腕上展示，科技感，旋转镜头",
    "negative_prompt": "模糊，抖动",
    "mode": "text2video",
    "ratio": "9:16",
    "resolution": "720p",
    "duration": 5,
    "num": 1,
    "with_audio": false
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "task_id": "vid_a1b2c3d4e5f67890",
        "status": "pending",
        "message": "视频生成任务已创建"
    }
}
```

### 查询任务状态
```http
GET /videos/generations/{task_id}
Authorization: Bearer {token}
```

### 获取任务列表
```http
GET /videos/generations?page=1&page_size=10
Authorization: Bearer {token}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 状态码

### 任务状态
- `pending`: 排队中
- `processing`: 生成中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消
