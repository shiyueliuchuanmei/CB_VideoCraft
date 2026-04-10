"""
认证路由
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.database import get_db
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic 模型
class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    avatar: str


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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
    
    # TODO: 从数据库查询用户
    # user = await db.get(User, int(user_id))
    # if user is None:
    #     raise credentials_exception
    # return user
    return {"id": int(user_id), "email": "user@example.com"}  # 临时返回


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # TODO: 检查邮箱是否已存在
    # result = await db.execute(select(User).where(User.email == user_data.email))
    # if result.scalar_one_or_none():
    #     raise HTTPException(status_code=400, detail="邮箱已注册")
    
    # TODO: 创建用户
    # user = User(
    #     email=user_data.email,
    #     name=user_data.name,
    #     hashed_password=get_password_hash(user_data.password),
    # )
    # db.add(user)
    # await db.commit()
    
    return {"code": 200, "message": "注册成功"}


@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # TODO: 验证用户
    # result = await db.execute(select(User).where(User.email == form_data.username))
    # user = result.scalar_one_or_none()
    
    # if not user or not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=400, detail="邮箱或密码错误")
    
    # TODO: 更新最后登录时间
    # user.last_login = datetime.utcnow()
    # await db.commit()
    
    # 临时逻辑
    access_token = create_access_token(data={"sub": "1"})
    return {
        "code": 200,
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": form_data.username,
                "name": "用户",
                "avatar": "",
            }
        }
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {"code": 200, "data": current_user}
