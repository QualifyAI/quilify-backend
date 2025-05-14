from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from typing import List, Optional

from app.services.resume_service import ResumeService
from app.models.resume import Resume
from app.models.user import User
from app.api.dependencies.auth import get_current_active_user
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeResponse, ResumeListResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_service = ResumeService()


@router.post("", response_model=ResumeResponse)
async def upload_resume(
    title: str = Form(...),
    resume_file: UploadFile = File(...),
    is_primary: bool = Form(False),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new resume file and extract its text content.
    """
    print("before resume upload")
    resume = await resume_service.upload_resume(
        user_id=str(current_user.id),
        title=title,
        file=resume_file,
        is_primary=is_primary
    )
    print("after resume upload")
    return ResumeResponse(
        id=resume.id,
        title=resume.title,
        content=resume.content,
        file_name=resume.file_name,
        is_primary=resume.is_primary,
        created_at=str(resume.created_at),
        updated_at=str(resume.updated_at) if resume.updated_at else None
    )


@router.post("/text", response_model=ResumeResponse)
async def save_resume_text(
    resume: ResumeCreate = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save resume text directly without file upload.
    """
    resume_data = await resume_service.save_resume_text(
        user_id=str(current_user.id),
        title=resume.title,
        content=resume.content,
        is_primary=resume.is_primary
    )
    
    return ResumeResponse(
        id=resume_data.id,
        title=resume_data.title,
        content=resume_data.content,
        file_name=resume_data.file_name,
        is_primary=resume_data.is_primary,
        created_at=str(resume_data.created_at),
        updated_at=str(resume_data.updated_at) if resume_data.updated_at else None
    )


@router.get("", response_model=ResumeListResponse)
async def get_user_resumes(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all resumes for the current user.
    """
    resumes = await resume_service.get_user_resumes(str(current_user.id))
    
    response_items = [
        ResumeResponse(
            id=resume.id,
            title=resume.title,
            content=resume.content,
            file_name=resume.file_name,
            is_primary=resume.is_primary,
            created_at=str(resume.created_at),
            updated_at=str(resume.updated_at) if resume.updated_at else None
        )
        for resume in resumes
    ]
    
    return ResumeListResponse(
        resumes=response_items,
        total=len(response_items)
    )


@router.get("/primary", response_model=Optional[ResumeResponse])
async def get_primary_resume(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the primary resume for the current user.
    """
    resume = await resume_service.get_primary_resume(str(current_user.id))
    
    if not resume:
        return None
    
    return ResumeResponse(
        id=resume.id,
        title=resume.title,
        content=resume.content,
        file_name=resume.file_name,
        is_primary=resume.is_primary,
        created_at=str(resume.created_at),
        updated_at=str(resume.updated_at) if resume.updated_at else None
    )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific resume by ID.
    """
    resume = await resume_service.get_resume(resume_id)
    
    # Check if resume belongs to current user
    if resume.userId != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )
    
    return ResumeResponse(
        id=resume.id,
        title=resume.title,
        content=resume.content,
        file_name=resume.file_name,
        is_primary=resume.is_primary,
        created_at=str(resume.created_at),
        updated_at=str(resume.updated_at) if resume.updated_at else None
    )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    resume_update: ResumeUpdate = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a resume.
    """
    # First check if resume exists and belongs to user
    original_resume = await resume_service.get_resume(resume_id)
    if original_resume.userId != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this resume"
        )
    
    # Update only provided fields
    update_data = {k: v for k, v in resume_update.model_dump().items() if v is not None}
    
    updated_resume = await resume_service.update_resume(resume_id, update_data)
    
    return ResumeResponse(
        id=updated_resume.id,
        title=updated_resume.title,
        content=updated_resume.content,
        file_name=updated_resume.file_name,
        is_primary=updated_resume.is_primary,
        created_at=str(updated_resume.created_at),
        updated_at=str(updated_resume.updated_at) if updated_resume.updated_at else None
    )


@router.put("/{resume_id}/set-primary", response_model=ResumeResponse)
async def set_primary_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Set a resume as the primary resume for the current user.
    """
    updated_resume = await resume_service.set_primary_resume(
        user_id=str(current_user.id),
        resume_id=resume_id
    )
    
    return ResumeResponse(
        id=updated_resume.id,
        title=updated_resume.title,
        content=updated_resume.content,
        file_name=updated_resume.file_name,
        is_primary=updated_resume.is_primary,
        created_at=str(updated_resume.created_at),
        updated_at=str(updated_resume.updated_at) if updated_resume.updated_at else None
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a resume.
    """
    # First check if resume exists and belongs to user
    original_resume = await resume_service.get_resume(resume_id)
    if original_resume.userId != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this resume"
        )
    
    success = await resume_service.delete_resume(resume_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume"
        ) 