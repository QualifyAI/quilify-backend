from typing import Dict, List, Any, Optional
from fastapi import HTTPException, status

from app.db.repositories.learning_path_repository import LearningPathRepository
from app.models.learning_path import LearningPath, Niche, PathQuestion
from .learning_path_ai_service import LearningPathAIService

class LearningPathService:
    """Service for managing learning path operations"""
    
    def __init__(self):
        self.repository = LearningPathRepository()
        self.ai_service = LearningPathAIService()
    
    async def get_all_niches(self) -> List[Niche]:
        """
        Get all available niches for learning paths
        
        Returns:
            List of Niche objects
        """
        return await self.repository.get_all_niches()
    
    async def get_questions_for_niche(self, niche_id: int, use_ai: bool = True) -> List[PathQuestion]:
        """
        Get questions to customize a learning path for a specific niche
        
        Args:
            niche_id: ID of the niche to get questions for
            use_ai: If true, generate questions using AI instead of database
            
        Returns:
            List of PathQuestion objects
        """
        # Get the niche name first
        niches = await self.repository.get_all_niches()
        niche = next((n for n in niches if n.id == niche_id), None)
        
        if not niche:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Niche with ID {niche_id} not found"
            )
        
        if use_ai:
            # Generate questions using AI
            return await self.ai_service.generate_questions_for_niche(niche.name)
        else:
            # Get pre-defined questions from database
            return await self.repository.get_questions_for_niche(niche_id)
    
    async def generate_learning_path(
        self, 
        niche_id: int, 
        custom_niche: Optional[str],
        answers: Dict[str, str]
    ) -> LearningPath:
        """
        Generate a learning path based on niche and user answers
        
        Args:
            niche_id: ID of the niche
            custom_niche: Custom niche name (if provided)
            answers: Dictionary of question IDs and selected answers
            
        Returns:
            Generated LearningPath object
        """
        # Get the niche name
        niche_name = custom_niche
        
        if not niche_name and niche_id > 0:
            niches = await self.repository.get_all_niches()
            niche = next((n for n in niches if n.id == niche_id), None)
            
            if not niche:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Niche with ID {niche_id} not found"
                )
                
            niche_name = niche.name
        
        if not niche_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either niche_id or custom_niche must be provided"
            )
        
        # Generate learning path using AI
        learning_path_data = await self.ai_service.generate_learning_path(
            niche_name=niche_name,
            answers=answers
        )
        
        # Create a LearningPath object
        return LearningPath.model_validate({
            "title": learning_path_data.title,
            "description": learning_path_data.description,
            "estimatedTime": learning_path_data.estimatedTime,
            "modules": learning_path_data.modules,
            "nicheId": niche_id,
            "customNiche": custom_niche if not niche_id or niche_id <= 0 else None
        })
    
    async def save_learning_path(self, user_id: str, learning_path_data: Dict[str, Any]) -> LearningPath:
        """
        Save a learning path for a user
        
        Args:
            user_id: ID of the user
            learning_path_data: Learning path data
            
        Returns:
            Saved LearningPath object
        """
        learning_path_data["userId"] = user_id
        return await self.repository.create_learning_path(learning_path_data)
    
    async def get_user_learning_paths(self, user_id: str) -> List[LearningPath]:
        """
        Get all learning paths for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of LearningPath objects
        """
        return await self.repository.get_learning_paths_by_user_id(user_id)
    
    async def get_learning_path(self, path_id: str) -> LearningPath:
        """
        Get a specific learning path
        
        Args:
            path_id: ID of the learning path
            
        Returns:
            LearningPath object
            
        Raises:
            HTTPException: If learning path is not found
        """
        learning_path = await self.repository.get_learning_path_by_id(path_id)
        
        if not learning_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
            
        return learning_path
    
    async def update_learning_path(self, path_id: str, update_data: Dict[str, Any]) -> LearningPath:
        """
        Update a learning path
        
        Args:
            path_id: ID of the learning path
            update_data: Dictionary of fields to update
            
        Returns:
            Updated LearningPath object
            
        Raises:
            HTTPException: If learning path is not found
        """
        updated_path = await self.repository.update_learning_path(path_id, update_data)
        
        if not updated_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
            
        return updated_path
    
    async def delete_learning_path(self, path_id: str) -> bool:
        """
        Delete a learning path
        
        Args:
            path_id: ID of the learning path
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If learning path is not found
        """
        path = await self.repository.get_learning_path_by_id(path_id)
        
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
            
        return await self.repository.delete_learning_path(path_id) 