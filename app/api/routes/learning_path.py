from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.services import LearningPathService
from app.models.learning_path import LearningPath, Niche, PathQuestion
from app.models.user import User
from app.schemas.learning_path import (
    NicheResponse, 
    LearningPathRequest, 
    LearningPathCreate,
    LearningPathOutput
)
from app.api.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])
learning_path_service = LearningPathService()

@router.get("/niches", response_model=List[Niche])
async def get_niches():
    """
    Get all available niches for learning paths
    """
    return await learning_path_service.get_all_niches()

@router.get("/questions", response_model=List[PathQuestion])
async def get_questions(nicheId: int, use_ai: bool = True):
    """
    Get questions to customize a learning path for a specific niche
    
    Parameters:
    - nicheId: ID of the niche to get questions for
    - use_ai: If true, generate questions using AI instead of database (default: true)
    """
    return await learning_path_service.get_questions_for_niche(nicheId, use_ai)

@router.post("/generate", response_model=LearningPathOutput)
async def generate_learning_path(
    request: LearningPathRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a learning path based on niche and user answers
    """
    # Debug log to check user authentication
    print(f"Generating learning path for user: {current_user.email}")
    
    return await learning_path_service.generate_learning_path(
        request.nicheId,
        request.customNiche,
        request.answers
    )

@router.post("/save", response_model=LearningPath)
async def save_learning_path(
    path: LearningPathCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a learning path for a user
    """
    return await learning_path_service.save_learning_path(
        str(current_user.id),
        path.model_dump()
    )

@router.get("/user", response_model=List[LearningPath])
async def get_user_learning_paths(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all learning paths for the current user
    """
    return await learning_path_service.get_user_learning_paths(str(current_user.id))

@router.get("/{path_id}", response_model=LearningPath)
async def get_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific learning path
    """
    path = await learning_path_service.get_learning_path(path_id)
    
    # Check if path belongs to user
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this learning path"
        )
    
    return path

@router.put("/{path_id}", response_model=LearningPath)
async def update_learning_path(
    path_id: str,
    update_data: LearningPathCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    return await learning_path_service.update_learning_path(
        path_id,
        update_data.model_dump()
    )

@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this learning path"
        )
    
    success = await learning_path_service.delete_learning_path(path_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete learning path"
        ) 