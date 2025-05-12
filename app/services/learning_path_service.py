from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

from app.db.repositories.learning_path_repository import LearningPathRepository
from app.models.learning_path import LearningPath, LearningPathInDB, Niche, PathQuestion
from app.services.ai_service import AIService


class LearningPathService:
    def __init__(self):
        self.repository = LearningPathRepository()
        self.ai_service = AIService()
    
    async def get_all_niches(self) -> List[Niche]:
        """
        Get all available niches for learning paths
        """
        return await self.repository.get_all_niches()
    
    async def get_questions_for_niche(self, niche_id: int) -> List[PathQuestion]:
        """
        Get questions to customize a learning path for a specific niche
        """
        # Check if niche exists
        niche = await self.repository.get_niche_by_id(niche_id)
        if not niche:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Niche with ID {niche_id} not found"
            )
        
        return await self.repository.get_questions_for_niche(niche_id)
    
    async def generate_learning_path(
        self, 
        niche_id: int, 
        custom_niche: Optional[str], 
        answers: Dict[str, str]
    ) -> LearningPath:
        """
        Generate a learning path based on niche and user answers
        """
        # Determine niche name
        niche_name = custom_niche
        if not custom_niche:
            niche = await self.repository.get_niche_by_id(niche_id)
            if not niche:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Niche with ID {niche_id} not found"
                )
            niche_name = niche.name
        
        # Generate learning path using AI service - now sync call without await
        path_data = self.ai_service.generate_learning_path(niche_name, answers)
        
        # Import datetime here to keep the imports at the top clean
        from datetime import datetime
        current_time = datetime.utcnow()
        
        # Return the generated path (not saved to database yet)
        return LearningPath(
            id="",  # Temporary ID
            userId="",  # Will be set when saved
            createdAt=current_time,  # Use current UTC time instead of None
            updatedAt=current_time,  # Use current UTC time instead of None
            **path_data.model_dump()
        )
    
    async def save_learning_path(self, user_id: str, path_data: Dict[str, Any]) -> LearningPath:
        """
        Save a generated learning path to database
        """
        path_in_db = await self.repository.create_path(user_id, path_data)
        return self._convert_to_path(path_in_db)
    
    async def get_learning_path(self, path_id: str) -> LearningPath:
        """
        Get a learning path by ID
        """
        path = await self.repository.get_path_by_id(path_id)
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
        
        return self._convert_to_path(path)
    
    async def get_user_learning_paths(self, user_id: str) -> List[LearningPath]:
        """
        Get all learning paths for a user
        """
        paths = await self.repository.get_paths_by_user_id(user_id)
        return [self._convert_to_path(path) for path in paths]
    
    async def update_learning_path(self, path_id: str, update_data: Dict[str, Any]) -> LearningPath:
        """
        Update a learning path
        """
        # Check if path exists
        path = await self.repository.get_path_by_id(path_id)
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
        
        updated_path = await self.repository.update_path(path_id, update_data)
        return self._convert_to_path(updated_path)
    
    async def delete_learning_path(self, path_id: str) -> bool:
        """
        Delete a learning path
        """
        # Check if path exists
        path = await self.repository.get_path_by_id(path_id)
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
        
        return await self.repository.delete_path(path_id)
    
    def _convert_to_path(self, path_in_db: LearningPathInDB) -> LearningPath:
        """
        Convert LearningPathInDB to LearningPath
        """
        path_dict = {
            "id": str(path_in_db.id),
            "userId": str(path_in_db.userId),
            "title": path_in_db.title,
            "description": path_in_db.description,
            "estimatedTime": path_in_db.estimatedTime,
            "modules": path_in_db.modules,
            "niche": path_in_db.niche,
            "createdAt": path_in_db.createdAt,
            "updatedAt": path_in_db.updatedAt
        }
        return LearningPath.model_validate(path_dict)
