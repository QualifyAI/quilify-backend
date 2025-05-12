from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import MongoDB
from app.models.user import UserInDB
from app.core.security import get_password_hash

class UserRepository:
    collection_name = "users"
    
    @property
    def collection(self):
        return MongoDB.get_db()[self.collection_name]
    
    async def get_by_id(self, id: str) -> Optional[UserInDB]:
        """
        Get user by ID
        """
        if not ObjectId.is_valid(id):
            return None
            
        user = await self.collection.find_one({"_id": ObjectId(id)})
        if user:
            return UserInDB.model_validate(user)
        return None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email
        """
        user = await self.collection.find_one({"email": email})
        if user:
            return UserInDB.model_validate(user)
        return None
    
    async def create(self, user_data: Dict[str, Any]) -> UserInDB:
        """
        Create a new user
        """
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        user_data["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(user_data)
        
        # Create a new user dict with the inserted document
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        
        return UserInDB.model_validate(created_user)
    
    async def update(self, id: str, update_data: Dict[str, Any]) -> Optional[UserInDB]:
        """
        Update user
        """
        if not ObjectId.is_valid(id):
            return None
            
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """
        Delete user
        """
        if not ObjectId.is_valid(id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0 