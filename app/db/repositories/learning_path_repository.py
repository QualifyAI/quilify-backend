from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from app.db.mongodb import MongoDB
from app.models.learning_path import LearningPathInDB, Niche, PathQuestion


class LearningPathRepository:
    path_collection_name = "learning_paths"
    niche_collection_name = "niches"
    question_collection_name = "path_questions"
    
    @property
    def path_collection(self):
        return MongoDB.get_db()[self.path_collection_name]
    
    @property
    def niche_collection(self):
        return MongoDB.get_db()[self.niche_collection_name]
    
    @property
    def question_collection(self):
        return MongoDB.get_db()[self.question_collection_name]
    
    async def get_path_by_id(self, id: str) -> Optional[LearningPathInDB]:
        """
        Get learning path by ID
        """
        if not ObjectId.is_valid(id):
            return None
            
        path = await self.path_collection.find_one({"_id": ObjectId(id)})
        if path:
            return LearningPathInDB.model_validate(path)
        return None
    
    async def get_paths_by_user_id(self, user_id: str) -> List[LearningPathInDB]:
        """
        Get all learning paths for a user
        """
        if not ObjectId.is_valid(user_id):
            return []
            
        cursor = self.path_collection.find({"userId": ObjectId(user_id)})
        paths = await cursor.to_list(length=100)
        return [LearningPathInDB.model_validate(path) for path in paths]
    
    async def create_path(self, user_id: str, path_data: Dict[str, Any]) -> LearningPathInDB:
        """
        Create a new learning path
        """
        path_data["userId"] = ObjectId(user_id)
        path_data["createdAt"] = datetime.utcnow()
        
        result = await self.path_collection.insert_one(path_data)
        
        # Get the created path
        created_path = await self.path_collection.find_one({"_id": result.inserted_id})
        
        return LearningPathInDB.model_validate(created_path)
    
    async def update_path(self, id: str, update_data: Dict[str, Any]) -> Optional[LearningPathInDB]:
        """
        Update learning path
        """
        if not ObjectId.is_valid(id):
            return None
            
        update_data["updatedAt"] = datetime.utcnow()
        await self.path_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return await self.get_path_by_id(id)
    
    async def delete_path(self, id: str) -> bool:
        """
        Delete learning path
        """
        if not ObjectId.is_valid(id):
            return False
            
        result = await self.path_collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def get_all_niches(self) -> List[Niche]:
        """
        Get all available niches
        """
        cursor = self.niche_collection.find()
        niches = await cursor.to_list(length=100)
        return [Niche.model_validate(niche) for niche in niches]
    
    async def get_niche_by_id(self, id: int) -> Optional[Niche]:
        """
        Get niche by ID
        """
        niche = await self.niche_collection.find_one({"id": id})
        if niche:
            return Niche.model_validate(niche)
        return None
    
    async def get_questions_for_niche(self, niche_id: int) -> List[PathQuestion]:
        """
        Get questions for a specific niche
        """
        cursor = self.question_collection.find({"nicheId": niche_id})
        questions = await cursor.to_list(length=50)
        return [PathQuestion.model_validate(q) for q in questions] 