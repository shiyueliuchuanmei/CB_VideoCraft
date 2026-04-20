"""
CC_VideoCraft 后端入口文件
"""
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import auth, users, images, videos, tasks
from app.routers.auth import get_current_user
from app.utils.storage import save_file, generate_filename, ensure_directory

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="电商视频智能创作平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(images.router, prefix="/api/images", tags=["图片"])
app.include_router(videos.router, prefix="/api/videos", tags=["视频"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务"])


# 文件上传接口
@app.post("/api/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """上传文件"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 检查文件大小（最大 10MB）
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    # 确保上传目录存在
    ensure_directory(settings.LOCAL_STORAGE_PATH)

    # 保存文件
    relative_url = await save_file(content, file.filename, folder="uploads")

    # 构造完整的 URL（用于外部 API 访问）
    # 获取请求的 host 和协议
    scheme = request.headers.get('x-forwarded-proto', 'http')
    host = request.headers.get('host', f'{settings.HOST}:{settings.PORT}')
    full_url = f"{scheme}://{host}{relative_url}"

    return {"code": 200, "data": {"url": full_url}}


# 静态文件
os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    await init_db()
    print(f"[OK] {settings.APP_NAME} started successfully!")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
