"""
任务管理路由
"""
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_task_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取任务统计"""
    try:
        # 查询总数
        total_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id"),
            {"user_id": current_user["id"]}
        )
        total = total_result.scalar()
        
        # 查询今日数量
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND created_at >= :today"),
            {"user_id": current_user["id"], "today": today}
        )
        today_count = today_result.scalar()
        
        return {
            "code": 200,
            "data": {
                "total": total,
                "today": today_count,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_tasks(
    page: int = 1,
    page_size: int = 10,
    task_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    try:
        where = "WHERE user_id = :user_id"
        params = {"user_id": current_user["id"]}
        
        if task_type:
            where += " AND task_type = :task_type"
            params["task_type"] = task_type
        
        # 查询总数
        count_result = await db.execute(
            text(f"SELECT COUNT(*) FROM tasks {where}"),
            params
        )
        total = count_result.scalar()
        
        # 查询列表
        offset = (page - 1) * page_size
        result = await db.execute(
            text(f"SELECT * FROM tasks {where} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {**params, "limit": page_size, "offset": offset}
        )
        
        items = []
        for row in result.fetchall():
            items.append({
                "task_id": row.task_id,
                "task_type": row.task_type,
                "status": row.status,
                "model": row.model,
                "prompt": row.prompt[:50] + "..." if len(row.prompt) > 50 else row.prompt,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })
        
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
