"""
FastAPI 依赖注入函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.config import settings
from backend.schemas.auth import TokenData
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    验证 JWT Token 并返回当前用户
    
    Args:
        credentials: HTTP Authorization Bearer Token
    
    Returns:
        TokenData: 用户信息
    
    Raises:
        HTTPException: 401 如果 token 无效
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
        
        token_data = TokenData(username=username, user_id=user_id)
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    验证用户是否处于活跃状态
    
    Args:
        current_user: 当前用户信息
    
    Returns:
        TokenData: 活跃用户信息
    
    Raises:
        HTTPException: 400 如果用户未激活
    """
    # Phase 1: 简化版本，所有用户都是活跃的
    # Phase 2: 从数据库查询用户状态
    return current_user


# 可选：需要管理员权限的依赖
async def get_current_admin_user(
    current_user: TokenData = Depends(get_current_active_user)
) -> TokenData:
    """
    验证用户是否有管理员权限
    
    Args:
        current_user: 当前用户信息
    
    Returns:
        TokenData: 管理员用户信息
    
    Raises:
        HTTPException: 403 如果用户不是管理员
    """
    # Phase 1: 简化版本，username 为 "admin" 的用户是管理员
    # Phase 2: 从数据库查询用户角色
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user
