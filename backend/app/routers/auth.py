"""
认证路由
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.feishu import feishu_service
from pydantic import BaseModel, EmailStr
import secrets

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic 模型
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    avatar: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用")
    return user


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已注册")

    # 创建用户
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 自动登录，返回 token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "code": 200,
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }
    }


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # 验证用户
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")

    # 更新最后登录时间
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "code": 200,
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {"code": 200, "data": current_user.to_dict()}


@router.get("/feishu/authorize", response_model=dict)
async def feishu_authorize():
    """获取飞书授权 URL"""
    state = secrets.token_urlsafe(16)
    auth_url = feishu_service.get_authorization_url(state)
    return {"code": 200, "data": {"url": auth_url}}


@router.post("/feishu/callback", response_model=dict)
async def feishu_callback(code: str, db: AsyncSession = Depends(get_db)):
    """飞书 OAuth 回调处理"""
    if not code:
        raise HTTPException(status_code=400, detail="缺少授权码")

    try:
        token_data = await feishu_service.get_access_token(code)
        access_token = token_data.get("access_token")

        user_info = await feishu_service.get_user_info(access_token)
        feishu_union_id = user_info.get("union_id")
        name = user_info.get("name", "飞书用户")
        avatar = user_info.get("avatar_url", "")
        email = user_info.get("email", "")

        result = await db.execute(select(User).where(User.feishu_union_id == feishu_union_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                email=email or None,
                name=name,
                feishu_union_id=feishu_union_id,
                avatar=avatar,
            )
            db.add(user)
        else:
            user.name = name
            user.avatar = avatar
            if email:
                user.email = email

        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "code": 200,
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": user.to_dict(),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"飞书登录失败: {str(e)}")
