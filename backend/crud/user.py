"""
用户 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.user import UserModel
from backend.schemas.auth import UserRegister
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCRUD:
    """用户的 CRUD 操作"""
    
    async def create(
        self, 
        db: AsyncSession, 
        user_in: UserRegister
    ) -> UserModel:
        """创建新用户"""
        hashed_password = pwd_context.hash(user_in.password)
        
        user = UserModel(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_by_username(
        self, 
        db: AsyncSession, 
        username: str
    ) -> Optional[UserModel]:
        """通过用户名获取用户"""
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(
        self, 
        db: AsyncSession, 
        email: str
    ) -> Optional[UserModel]:
        """通过邮箱获取用户"""
        if not email:
            return None
        result = await db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> Optional[UserModel]:
        """通过ID获取用户"""
        return await db.get(UserModel, user_id)
        
    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[UserModel]:
        """验证用户登录"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
            
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user

# 创建全局实例
user_crud = UserCRUD()
