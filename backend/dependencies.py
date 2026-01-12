"""
FastAPI 依赖注入函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config import settings
from backend.schemas.auth import TokenData
from backend.database import get_db
from backend.crud.user import user_crud
from backend.models.user import UserModel
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """
    验证 JWT Token 并返回当前用户数据
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        # 解码 JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None:
            raise credentials_exception
            
        # 验证用户是否存在于数据库
        user = await user_crud.get(db, user_id)
        if not user:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id)
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception


async def get_current_user_obj(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    获取当前用户对象（包含完整数据库信息）
    """
    user = await user_crud.get(db, current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """
    验证用户是否处于活跃状态
    """
    user = await user_crud.get(db, current_user.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """
    验证用户是否有管理员权限
    """
    user = await user_crud.get(db, current_user.user_id)
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
