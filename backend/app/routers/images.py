"""
图片生成路由
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
from app.services.doubao import generate_image, check_task_status

router = APIRouter()


# 请求模型
class ImageGenerationRequest(BaseModel):
    model: str = "seedream-2-0"
    prompt: str
    negative_prompt: str = ""
    mode: str = "text2image"  # text2image, image2image
    ratio: str = "1:1"
    resolution: str = "1024"
    num: int = 1
    image_url: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str


@router.get("/models")
async def get_image_models():
    """获取可用的图片模型列表"""
    return {
        "code": 200,
        "data": [
            {
                "id": "seedream-2-0",
                "name": "Seedream 2.0",
                "description": "豆包图片生成模型",
                "supported_ratios": ["1:1", "9:16", "16:9", "3:4", "4:3"],
                "supported_resolutions": ["512", "768", "1024", "2048"],
            },
            {
                "id": "seedream-2-0-pro",
                "name": "Seedream 2.0 Pro",
                "description": "豆包图片生成模型专业版",
                "supported_ratios": ["1:1", "9:16", "16:9", "3:4", "4:3"],
                "supported_resolutions": ["512", "768", "1024", "2048"],
            },
        ]
    }


@router.post("/generations", response_model=dict)
async def create_image_generation(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建图片生成任务"""
    task_id = f"img_{uuid.uuid4().hex[:16]}"
    
    try:
        # 保存任务到数据库
        await db.execute(
            text("""
            INSERT INTO tasks (
                task_id, task_type, status, model, prompt, negative_prompt,
                mode, ratio, resolution, num, input_image_url, user_id, created_at, updated_at
            ) VALUES (
                :task_id, :task_type, :status, :model, :prompt, :negative_prompt,
                :mode, :ratio, :resolution, :num, :input_image_url, :user_id, :created_at, :updated_at
            )
            """),
            {
                "task_id": task_id,
                "task_type": "image",
                "status": "pending",
                "model": request.model,
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "mode": request.mode,
                "ratio": request.ratio,
                "resolution": request.resolution,
                "num": request.num,
                "input_image_url": request.image_url if request.mode == "image2image" else None,
                "user_id": current_user["id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        await db.commit()
        
        # 异步执行生成任务
        background_tasks.add_task(
            generate_image,
            task_id=task_id,
            model=request.model,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            mode=request.mode,
            ratio=request.ratio,
            resolution=request.resolution,
            num=request.num,
            image_url=request.image_url,
            user_id=current_user["id"]
        )
        
        return {
            "code": 200,
            "data": {
                "task_id": task_id,
                "status": "pending",
                "message": "图片生成任务已创建"
            }
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/generations/{task_id}")
async def get_image_generation(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查询图片生成任务"""
    try:
        result = await db.execute(
            text("""
            SELECT * FROM tasks 
            WHERE task_id = :task_id AND user_id = :user_id AND task_type = 'image'
            """),
            {"task_id": task_id, "user_id": current_user["id"]}
        )
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 如果任务在处理中，查询最新状态
        if row.status == "processing":
            status_info = await check_task_status(task_id, "image")
        
        return {
            "code": 200,
            "data": {
                "task_id": row.task_id,
                "status": row.status,
                "progress": _calculate_progress(row.status),
                "model": row.model,
                "prompt": row.prompt,
                "negative_prompt": row.negative_prompt,
                "mode": row.mode,
                "ratio": row.ratio,
                "resolution": row.resolution,
                "num": row.num,
                "output_urls": json.loads(row.output_urls) if row.output_urls else [],
                "error_message": row.error_message,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询任务失败: {str(e)}")


@router.get("/generations")
async def list_image_generations(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取图片生成任务列表"""
    try:
        # 构建查询条件
        where_clause = "WHERE user_id = :user_id AND task_type = 'image'"
        params = {"user_id": current_user["id"]}
        
        if status:
            where_clause += " AND status = :status"
            params["status"] = status
        
        # 查询总数
        count_result = await db.execute(
            text(f"SELECT COUNT(*) as total FROM tasks {where_clause}"),
            params
        )
        total = count_result.scalar()
        
        # 查询任务列表
        offset = (page - 1) * page_size
        result = await db.execute(
            text(f"""
            SELECT * FROM tasks {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """),
            {**params, "limit": page_size, "offset": offset}
        )
        
        tasks = []
        for row in result.fetchall():
            tasks.append({
                "task_id": row.task_id,
                "status": row.status,
                "model": row.model,
                "prompt": row.prompt[:100] + "..." if len(row.prompt) > 100 else row.prompt,
                "mode": row.mode,
                "ratio": row.ratio,
                "resolution": row.resolution,
                "num": row.num,
                "output_urls": json.loads(row.output_urls) if row.output_urls else [],
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            })
        
        return {
            "code": 200,
            "data": {
                "items": tasks,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询任务列表失败: {str(e)}")


@router.post("/generations/{task_id}/cancel")
async def cancel_image_generation(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消图片生成任务"""
    try:
        # 查询任务
        result = await db.execute(
            text("""
            SELECT * FROM tasks 
            WHERE task_id = :task_id AND user_id = :user_id AND task_type = 'image'
            """),
            {"task_id": task_id, "user_id": current_user["id"]}
        )
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 只能取消待处理或处理中的任务
        if row.status not in ["pending", "processing"]:
            raise HTTPException(status_code=400, detail=f"任务状态为 {row.status}，无法取消")
        
        # 更新任务状态
        await db.execute(
            text("""
            UPDATE tasks 
            SET status = 'cancelled', updated_at = :updated_at
            WHERE task_id = :task_id
            """),
            {"task_id": task_id, "updated_at": datetime.utcnow()}
        )
        await db.commit()
        
        return {"code": 200, "message": "任务已取消"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.delete("/generations/{task_id}")
async def delete_image_generation(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除图片生成任务"""
    try:
        # 查询任务是否存在
        result = await db.execute(
            text("""
            SELECT * FROM tasks 
            WHERE task_id = :task_id AND user_id = :user_id AND task_type = 'image'
            """),
            {"task_id": task_id, "user_id": current_user["id"]}
        )
        
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 删除任务
        await db.execute(
            text("""
            DELETE FROM tasks 
            WHERE task_id = :task_id AND user_id = :user_id
            """),
            {"task_id": task_id, "user_id": current_user["id"]}
        )
        await db.commit()
        
        return {"code": 200, "message": "任务已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


def _calculate_progress(status: str) -> int:
    """根据状态计算进度"""
    progress_map = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "failed": 0,
        "cancelled": 0,
    }
    return progress_map.get(status, 0)
