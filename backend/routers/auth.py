"""
认证相关的 API 路由
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import logging

from backend.config import settings
from backend.schemas.auth import UserLogin, UserRegister, Token, UserResponse
from backend.dependencies import get_current_user
from backend.schemas.auth import TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Phase 1: 简化版本 - 使用内存存储用户
# Phase 2: 升级为数据库存储
# 预生成的密码哈希（避免启动时计算）
# admin123: $2b$12$... 
# demo123: $2b$12$...
FAKE_USERS_DB = {
    "admin": {
        "id": "user-001",
        "username": "admin",
        "email": "admin@example.com",
        # 密码: admin123
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU2JYY.JdFSa",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    "demo": {
        "id": "user-002",
        "username": "demo",
        "email": "demo@example.com",
        # 密码: demo123
        "hashed_password": "$2b$12$KIXbJcc1YBfFRRxJ0F5aUO.4Tk1SaF9Gz7U3dMZQHGBkZL9Jg9o4W",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    创建 JWT access token
    
    Args:
        data: 要编码的数据（通常包含用户名、用户ID等）
        expires_delta: 过期时间（可选）
    
    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    """
    注册新用户
    
    Args:
        user: 用户注册信息
    
    Returns:
        UserResponse: 创建的用户信息
    """
    # 检查用户名是否已存在
    if user.username in FAKE_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建新用户
    user_id = f"user-{len(FAKE_USERS_DB) + 1:03d}"
    FAKE_USERS_DB[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"New user registered: {user.username}")
    
    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        is_active=True,
        created_at=datetime.utcnow().isoformat()
    )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    用户登录
    
    Args:
        user_login: 登录凭证
    
    Returns:
        Token: JWT token 和过期时间
    """
    # 验证用户
    user = FAKE_USERS_DB.get(user_login.username)
    
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 创建 access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user_login.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user)
):
    """
    获取当前登录用户的信息
    
    Args:
        current_user: 当前用户（从 JWT token 解析）
    
    Returns:
        UserResponse: 用户信息
    """
    # 从数据库获取用户详细信息
    user = FAKE_USERS_DB.get(current_user.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    用户登出
    
    注意：JWT 是无状态的，服务端不存储 token
    真正的登出需要在客户端删除 token
    Phase 2 可以实现 token 黑名单机制
    
    Args:
        current_user: 当前用户
    
    Returns:
        成功消息
    """
    logger.info(f"User logged out: {current_user.username}")
    
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }
