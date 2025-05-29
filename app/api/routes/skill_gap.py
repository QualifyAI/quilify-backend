from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from typing import List, Optional, Dict

from app.services import SkillGapService
from app.models.skill_gap import SkillGap, ProjectRecommendation, SkillGapAnalysisRequest
from app.schemas.skill_gap import SkillGapAnalysisOutput
from app.models.user import User
from app.api.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/skill-gap", tags=["skill gap analysis"])
skill_gap_service = SkillGapService()

@router.post("/analyze", response_model=SkillGapAnalysisOutput)
async def analyze_skill_gap(
    resume_id: str = Form(...),
    job_description: str = Form(...),
    job_posting_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze skill gap between a resume and job requirements
    
    This endpoint analyzes the skill gap using a previously stored resume.
    The analysis is automatically saved to the user's history.
    """
    
    # Perform the analysis and save it to the database
    return await skill_gap_service.analyze_skill_gap(
        user_id=str(current_user.id),
        resume_id=resume_id,
        job_description=job_description,
        job_posting_url=job_posting_url
    )

@router.post("/fetch-job-description")
async def fetch_job_description(
    data: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetch job description from a URL
    """
    if "job_posting_url" not in data or not data["job_posting_url"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job posting URL is required"
        )
    
    job_description = await skill_gap_service.fetch_job_description(data["job_posting_url"])
    
    if not job_description or job_description.startswith("Error fetching"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch job description from the provided URL"
        )
    
    return {"job_description": job_description}

@router.get("/history", response_model=List[SkillGap])
async def get_analysis_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all skill gap analyses for the current user
    """
    return await skill_gap_service.get_skill_gap_analyses(str(current_user.id))

@router.get("/history/{analysis_id}", response_model=SkillGap)
async def get_analysis_by_id(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific skill gap analysis
    """
    analysis = await skill_gap_service.get_skill_gap_analysis(analysis_id)
    
    # Check if the analysis belongs to the current user
    if str(analysis.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this analysis"
        )
    
    return analysis

@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a skill gap analysis
    """
    # Get the analysis to check ownership first
    analysis = await skill_gap_service.get_skill_gap_analysis(analysis_id)
    
    # Check if the analysis belongs to the current user
    if str(analysis.userId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this analysis"
        )
    
    # Delete the analysis
    success = await skill_gap_service.delete_skill_gap_analysis(analysis_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis"
        )

@router.post("/projects", response_model=List[ProjectRecommendation])
async def get_project_recommendations(
    skills: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate project recommendations based on missing skills
    """
    # This endpoint would typically call a specialized service method
    # For simplicity, we're using a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint is not yet implemented"
    ) 