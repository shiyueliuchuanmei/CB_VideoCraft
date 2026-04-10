"""
视频生成路由
"""
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.routers.auth import get_current_user
from app.services.doubao import generate_video, check_task_status

router = APIRouter()


class VideoGenerationRequest(BaseModel):
    model: str = "seedance-2-0"
    prompt: str
    negative_prompt: str = ""
    mode: str = "text2video"
    ratio: str = "9:16"
    resolution: str = "720p"
    duration: int = 5
    num: int = 1
    with_audio: bool = False
    image_url: Optional[str] = None


@router.get("/models")
async def get_video_models():
    """获取视频模型列表"""
    return {
        "code": 200,
        "data": [
            {
                "id": "seedance-2-0",
                "name": "Seedance 2.0",
                "description": "豆包视频生成模型",
                "supported_ratios": ["9:16", "16:9", "1:1"],
                "supported_resolutions": ["480p", "720p", "1080p"],
                "max_duration": 10,
            },
        ]
    }


@router.post("/generations")
async def create_video_generation(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建视频生成任务"""
    task_id = f"vid_{uuid.uuid4().hex[:16]}"
    
    try:
        await db.execute(
            text("""
            INSERT INTO tasks (task_id, task_type, status, model, prompt, user_id, created_at)
            VALUES (:task_id, 'video', 'pending', :model, :prompt, :user_id, :created_at)
            """),
            {
                "task_id": task_id,
                "model": request.model,
                "prompt": request.prompt,
                "user_id": current_user["id"],
                "created_at": datetime.utcnow(),
            }
        )
        await db.commit()
        
        background_tasks.add_task(
            generate_video,
            task_id=task_id,
            model=request.model,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            mode=request.mode,
            ratio=request.ratio,
            resolution=request.resolution,
            duration=request.duration,
            num=request.num,
            with_audio=request.with_audio,
            image_url=request.image_url,
            user_id=current_user["id"]
        )
        
        return {"code": 200, "data": {"task_id": task_id, "status": "pending"}}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations")
async def get_video_generations(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取视频生成任务列表"""
    try:
        user_id = current_user["id"]
        
        # 获取视频任务列表
        result = await db.execute(
            text("""
                SELECT task_id, prompt, status, model, created_at, completed_at, output_urls 
                FROM tasks 
                WHERE task_type = 'video' AND user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"user_id": user_id, "limit": page_size, "offset": (page - 1) * page_size}
        )
        
        tasks = []
        for row in result.fetchall():
            # 处理日期格式 - 可能是字符串或 datetime 对象
            from datetime import datetime
            created_at = row.created_at
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            completed_at = row.completed_at
            if isinstance(completed_at, datetime):
                completed_at = completed_at.isoformat()
            
            tasks.append({
                "id": row.task_id,
                "type": "video",
                "prompt": row.prompt,
                "status": row.status,
                "model": row.model,
                "created_at": created_at,
                "completed_at": completed_at,
                "url": row.output_urls,
            })
        
        return {
            "code": 200,
            "data": {
                "tasks": tasks,
                "total": len(tasks),
                "page": page,
                "page_size": page_size,
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in get_video_generations: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations/{task_id}")
async def get_video_generation(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查询视频生成任务"""
    result = await db.execute(
        text("SELECT * FROM tasks WHERE task_id = :task_id AND user_id = :user_id"),
        {"task_id": task_id, "user_id": current_user["id"]}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "code": 200,
        "data": {
            "task_id": row.task_id,
            "status": row.status,
            "model": row.model,
            "prompt": row.prompt,
        }
    }
