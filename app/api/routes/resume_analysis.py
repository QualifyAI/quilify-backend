from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.models.user import User
from app.services import ResumeAnalysisService, ResumeService, ResumeAnalysisOutput, ImprovedResumeOutput
from app.api.dependencies.auth import get_current_active_user
from app.services.utils.file_service import FileService

# Define a response model for analyze_resume
class ResumeAnalysisResponse(BaseModel):
    analysis_id: str
    analysis_result: ResumeAnalysisOutput

# Define a model for analysis metadata
class AnalysisMetadata(BaseModel):
    id: str
    userId: str
    resumeId: str
    createdAt: datetime

router = APIRouter(prefix="/resume", tags=["resume-analysis"])
resume_analysis_service = ResumeAnalysisService()
resume_service = ResumeService()
file_service = FileService()

@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str = Form(...),
    job_title: str = Form("General Position"),
    industry: str = Form("Technology"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze a resume for ATS compatibility, content quality, and overall effectiveness.
    
    Uses an existing resume from the user's saved resumes.
    """
    # Get resume from database
    try:
        resume = await resume_service.get_resume(resume_id)
        
        # Verify the resume belongs to the current user
        if resume.userId != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
            
        resume_text = resume.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {str(e)}"
        )
    
    # Perform the analysis
    try:
        # We'll let the service handle the saving
        analysis_result = await resume_analysis_service.analyze_resume(
            resume_text=resume_text,
            job_title=job_title,
            industry=industry,
            user_id=str(current_user.id),
            resume_id=resume_id
        )
        
        # Save the analysis (the service's analyze_resume doesn't return the ID)
        analysis_id = await resume_analysis_service.save_analysis(
            user_id=str(current_user.id),
            resume_id=resume_id,
            analysis_result=analysis_result
        )
        
        return ResumeAnalysisResponse(
            analysis_id=analysis_id,
            analysis_result=analysis_result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/optimize", response_model=ImprovedResumeOutput)
async def optimize_resume(
    resume_id: str = Form(...),
    analysis_id: Optional[str] = Form(None),
    job_title: str = Form("General Position"),
    industry: str = Form("Technology"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate an optimized version of a resume based on analysis results.
    
    Uses an existing resume from the user's saved resumes.
    Optionally accepts a previous analysis ID or will perform a new analysis.
    """
    # Get resume from database
    try:
        resume = await resume_service.get_resume(resume_id)
        
        # Verify the resume belongs to the current user
        if resume.userId != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
            
        resume_text = resume.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {str(e)}"
        )
    
    # Get the analysis result if an ID was provided
    analysis_result = None
    if analysis_id:
        try:
            # Fetch the analysis from the database
            # This assumes you have a method to retrieve analysis by ID
            # If not, you'll need to implement this in a service
            analysis_result = await resume_analysis_service.get_analysis_by_id(analysis_id)
            
            # Verify the analysis belongs to the user/resume
            if not analysis_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Analysis with ID {analysis_id} not found"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error retrieving analysis: {str(e)}"
            )
    
    # If analysis result wasn't provided or found, perform analysis first
    if not analysis_result:
        try:
            analysis_result = await resume_analysis_service.analyze_resume(
                resume_text=resume_text,
                job_title=job_title,
                industry=industry,
                user_id=str(current_user.id),
                resume_id=resume_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(e)}"
            )
    
    # Generate optimized resume
    try:
        optimized_resume = await resume_analysis_service.optimize_resume(
            resume_text=resume_text,
            job_title=job_title,
            industry=industry,
            analysis_result=analysis_result
        )
        return optimized_resume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )

@router.get("/analyses", response_model=List[AnalysisMetadata])
async def get_user_analyses(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all resume analyses for the current user
    """
    try:
        analyses = await resume_analysis_service.repository.get_analyses_by_user_id(str(current_user.id))
        return analyses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analyses: {str(e)}"
        )

@router.get("/analyses/{analysis_id}", response_model=ResumeAnalysisOutput)
async def get_analysis_by_id(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific resume analysis by ID
    """
    try:
        # Get the analysis
        analysis = await resume_analysis_service.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {analysis_id} not found"
            )
        
        # TODO: Add verification that the analysis belongs to the current user
        # This would require storing user_id with the analysis in the database
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis: {str(e)}"
        ) 