"""
用户路由
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user, verify_password, get_password_hash

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateSettingsRequest(BaseModel):
    doubao_api_key: Optional[str] = None
    storage_type: Optional[str] = None
    oss_config: Optional[str] = None


@router.get("/me")
async def get_user_info(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取用户信息"""
    return {"code": 200, "data": current_user.to_dict()}


@router.put("/me")
async def update_user_info(
    user_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    try:
        if user_data.name is not None:
            current_user.name = user_data.name
        if user_data.avatar is not None:
            current_user.avatar = user_data.avatar
        current_user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(current_user)
        return {"code": 200, "data": current_user.to_dict(), "message": "更新成功"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/me/password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码不正确")

    # 更新密码
    try:
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return {"code": 200, "message": "密码修改成功"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"密码修改失败: {str(e)}")


@router.get("/me/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户设置"""
    import json
    oss_config = {}
    if current_user.oss_config:
        try:
            oss_config = json.loads(current_user.oss_config)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "code": 200,
        "data": {
            "doubao_api_key": current_user.doubao_api_key or "",
            "storage_type": current_user.storage_type or "local",
            "oss_config": oss_config,
        }
    }


@router.put("/me/settings")
async def update_user_settings(
    settings_data: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户设置"""
    try:
        if settings_data.doubao_api_key is not None:
            current_user.doubao_api_key = settings_data.doubao_api_key
        if settings_data.storage_type is not None:
            current_user.storage_type = settings_data.storage_type
        if settings_data.oss_config is not None:
            current_user.oss_config = settings_data.oss_config
        current_user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return {"code": 200, "message": "设置已保存"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"设置保存失败: {str(e)}")
