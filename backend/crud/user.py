"""
User CRUD operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.user import UserModel
from backend.schemas.auth import UserRegister
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCRUD:
    """User CRUD operations"""
    
    async def create(
        self, 
        db: AsyncSession, 
        user_in: UserRegister
    ) -> UserModel:
        """Create new user"""
        hashed_password = pwd_context.hash(user_in.password)
        
        normalized_email = user_in.email or None
        user = UserModel(
            username=user_in.username,
            email=normalized_email,
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
        """Get user by username"""
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(
        self, 
        db: AsyncSession, 
        email: str
    ) -> Optional[UserModel]:
        """Get user by email"""
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
        """Get user by ID"""
        return await db.get(UserModel, user_id)
        
    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[UserModel]:
        """Verify user login"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
            
        # Update last login time
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[UserModel]:
        """Get all users"""
        result = await db.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def remove(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[UserModel]:
        """Delete user"""
        user = await self.get(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
        return user

# Create global instance
user_crud = UserCRUD()
