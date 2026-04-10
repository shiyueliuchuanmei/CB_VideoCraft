"""
用户路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def get_user_info(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取用户信息"""
    return {"code": 200, "data": current_user}


@router.put("/me")
async def update_user_info(
    user_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    # TODO: 实现更新逻辑
    return {"code": 200, "message": "更新成功"}


@router.post("/me/password")
async def change_password(
    password_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # TODO: 实现修改密码逻辑
    return {"code": 200, "message": "密码修改成功"}


@router.get("/me/settings")
async def get_user_settings(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户设置"""
    return {
        "code": 200,
        "data": {
            "api_key": "",
            "storage_type": "local",
        }
    }


@router.put("/me/settings")
async def update_user_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户设置"""
    # TODO: 实现更新逻辑
    return {"code": 200, "message": "设置已保存"}
