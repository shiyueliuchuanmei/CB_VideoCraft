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
        user_id = current_user.id

        # 查询总数
        total_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        total = total_result.scalar()

        # 查询今日数量
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND created_at >= :today"),
            {"user_id": user_id, "today": today}
        )
        today_count = today_result.scalar()

        # 今日图片数量
        today_images_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'image' AND created_at >= :today"),
            {"user_id": user_id, "today": today}
        )
        today_images = today_images_result.scalar()

        # 今日视频数量
        today_videos_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'video' AND created_at >= :today"),
            {"user_id": user_id, "today": today}
        )
        today_videos = today_videos_result.scalar()

        # 成功数量
        success_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND status = 'completed'"),
            {"user_id": user_id}
        )
        success_count = success_result.scalar()

        # 失败数量
        failed_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND status = 'failed'"),
            {"user_id": user_id}
        )
        failed_count = failed_result.scalar()

        # 总图片数量
        total_images_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'image'"),
            {"user_id": user_id}
        )
        total_images = total_images_result.scalar()

        # 总视频数量
        total_videos_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'video'"),
            {"user_id": user_id}
        )
        total_videos = total_videos_result.scalar()

        # 昨日数量（用于趋势计算）
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0) - timedelta(days=1)
        yesterday_images_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'image' AND created_at >= :yesterday AND created_at < :today"),
            {"user_id": user_id, "yesterday": yesterday, "today": today}
        )
        yesterday_images = yesterday_images_result.scalar()

        yesterday_videos_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'video' AND created_at >= :yesterday AND created_at < :today"),
            {"user_id": user_id, "yesterday": yesterday, "today": today}
        )
        yesterday_videos = yesterday_videos_result.scalar()

        # 计算趋势百分比
        image_trend = round(((today_images - yesterday_images) / yesterday_images) * 100, 1) if yesterday_images > 0 else (100 if today_images > 0 else 0)
        video_trend = round(((today_videos - yesterday_videos) / yesterday_videos) * 100, 1) if yesterday_videos > 0 else (100 if today_videos > 0 else 0)

        # 成功率
        success_rate = round((success_count / total) * 100, 1) if total > 0 else 0

        # 本周图片/视频数量
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0)
        week_images_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'image' AND created_at >= :week_start"),
            {"user_id": user_id, "week_start": week_start}
        )
        week_images = week_images_result.scalar()

        week_videos_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'video' AND created_at >= :week_start"),
            {"user_id": user_id, "week_start": week_start}
        )
        week_videos = week_videos_result.scalar()

        # 本月图片/视频数量
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        month_images_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'image' AND created_at >= :month_start"),
            {"user_id": user_id, "month_start": month_start}
        )
        month_images = month_images_result.scalar()

        month_videos_result = await db.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND task_type = 'video' AND created_at >= :month_start"),
            {"user_id": user_id, "month_start": month_start}
        )
        month_videos = month_videos_result.scalar()

        return {
            "code": 200,
            "data": {
                "total": total,
                "today": today_count,
                "today_images": today_images,
                "today_videos": today_videos,
                "total_images": total_images,
                "total_videos": total_videos,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": success_rate,
                "image_trend": image_trend,
                "video_trend": video_trend,
                "week_images": week_images,
                "week_videos": week_videos,
                "month_images": month_images,
                "month_videos": month_videos,
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
        params = {"user_id": current_user.id}
        
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
            import json as _json
            output_urls = _json.loads(row.output_urls) if row.output_urls else []
            created_at = row.created_at
            if hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()
            completed_at = row.completed_at
            if completed_at and hasattr(completed_at, 'isoformat'):
                completed_at = completed_at.isoformat()
            items.append({
                "task_id": row.task_id,
                "task_type": row.task_type,
                "status": row.status,
                "model": row.model,
                "prompt": row.prompt[:50] + "..." if len(row.prompt) > 50 else row.prompt,
                "mode": row.mode,
                "ratio": row.ratio,
                "output_urls": output_urls,
                "error_message": row.error_message,
                "created_at": created_at,
                "completed_at": completed_at,
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
