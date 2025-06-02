from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.services import LearningPathService
from app.models.learning_path import (
    LearningPath, 
    Niche, 
    PathQuestion, 
    ModuleProgressUpdate,
    ResourceProgressUpdate,
    CustomResourceAdd,
    LearningPathStats
)
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
    Get questions for tailoring learning path based on selected niche
    """
    return await learning_path_service.get_questions_for_niche(nicheId, use_ai)

@router.post("/generate", response_model=LearningPathOutput)
async def generate_learning_path(
    request: LearningPathRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a new learning path based on user's answers
    """
    return await learning_path_service.generate_learning_path(request)

@router.post("/save", response_model=LearningPath)
async def save_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a learning path to user's account
    """
    return await learning_path_service.save_learning_path(
        str(current_user.id),
        path_data.model_dump()
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

@router.delete("/{path_id}")
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    return {"message": "Learning path deleted successfully"}

# New Progress Tracking Endpoints

@router.put("/{path_id}/progress/module", response_model=LearningPath)
async def update_module_progress(
    path_id: str,
    progress_update: ModuleProgressUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update progress for a specific module in a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    return await learning_path_service.update_module_progress(
        path_id, 
        progress_update
    )

@router.put("/{path_id}/progress/resource", response_model=LearningPath)
async def update_resource_progress(
    path_id: str,
    progress_update: ResourceProgressUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update progress for a specific resource in a module
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    return await learning_path_service.update_resource_progress(
        path_id, 
        progress_update
    )

@router.post("/{path_id}/resources/custom", response_model=LearningPath)
async def add_custom_resource(
    path_id: str,
    custom_resource: CustomResourceAdd,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a custom resource to a module
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    return await learning_path_service.add_custom_resource(
        path_id, 
        custom_resource
    )

@router.get("/{path_id}/stats", response_model=LearningPathStats)
async def get_learning_path_stats(
    path_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed statistics for a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this learning path"
        )
    
    return await learning_path_service.calculate_path_stats(path_id)

@router.put("/{path_id}/notes")
async def update_path_notes(
    path_id: str,
    notes: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update custom notes for a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    await learning_path_service.update_path_notes(path_id, notes)
    return {"message": "Notes updated successfully"}

@router.put("/{path_id}/target-date")
async def update_target_completion_date(
    path_id: str,
    target_date: str,  # ISO format datetime string
    current_user: User = Depends(get_current_active_user)
):
    """
    Update target completion date for a learning path
    """
    # Check if path belongs to user
    path = await learning_path_service.get_learning_path(path_id)
    if str(path.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning path"
        )
    
    from datetime import datetime
    try:
        parsed_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
        await learning_path_service.update_target_completion_date(path_id, parsed_date)
        return {"message": "Target completion date updated successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"
        ) 