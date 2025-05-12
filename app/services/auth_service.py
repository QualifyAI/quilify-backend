from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.db.repositories.user_repository import UserRepository
from app.models.user import User, UserInDB
from app.schemas.auth import TokenPayload

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with email and password
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def create_token_for_user(self, user: UserInDB) -> Dict[str, str]:
        """
        Create access token for user
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id), 
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(self, token: str) -> Optional[UserInDB]:
        """
        Validate token and return current user
        """
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            token_data = TokenPayload.model_validate(payload)
            if token_data.sub is None:
                return None
        except JWTError:
            return None
        
        user = await self.user_repository.get_by_id(token_data.sub)
        if user is None:
            return None
        
        return user
    
    async def register_user(self, user_data: Dict[str, Any]) -> UserInDB:
        """
        Register a new user
        """
        # Check if user with email already exists
        existing_user = await self.user_repository.get_by_email(user_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        return await self.user_repository.create(user_data)
    
    def user_to_response(self, user: UserInDB) -> User:
        """
        Convert UserInDB to User model
        """
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        return User.model_validate(user_dict) 