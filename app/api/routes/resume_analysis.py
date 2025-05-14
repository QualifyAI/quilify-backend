from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from typing import Optional

from app.models.user import User
from app.services.resume_analysis_service import ResumeAnalysisService, ResumeAnalysisOutput, ImprovedResumeOutput
from app.services.resume_service import ResumeService
from app.api.dependencies.auth import get_current_active_user
from app.utils.resume_parser import parse_resume_file

router = APIRouter(prefix="/resume", tags=["resume-analysis"])
resume_analysis_service = ResumeAnalysisService()
resume_service = ResumeService()

@router.post("/analyze", response_model=ResumeAnalysisOutput)
async def analyze_resume(
    resume_file: Optional[UploadFile] = File(None),
    resume_id: Optional[str] = Form(None),
    job_title: str = Form("General Position"),
    industry: str = Form("Technology"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze a resume for ATS compatibility, content quality, and overall effectiveness.
    
    Can accept either a resume file upload or an existing resume ID.
    """
    # Check if we have at least one source
    if not resume_file and not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either resume_file or resume_id must be provided"
        )
    
    # Get resume text
    resume_text = ""
    
    if resume_id:
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
    
    elif resume_file:
        # Extract text from uploaded file
        try:
            resume_text = await parse_resume_file(resume_file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse resume file: {str(e)}"
            )
    
    # Perform the analysis
    try:
        analysis_result = await resume_analysis_service.analyze_resume(
            resume_text=resume_text,
            job_title=job_title,
            industry=industry
        )
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/optimize", response_model=ImprovedResumeOutput)
async def optimize_resume(
    analysis_id: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    resume_id: Optional[str] = Form(None),
    job_title: str = Form("General Position"),
    industry: str = Form("Technology"),
    analysis_result: Optional[ResumeAnalysisOutput] = Body(None),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate an optimized version of a resume based on analysis results.
    
    Can accept:
    - Either a resume file upload or an existing resume ID
    - Either an analysis result object or will perform a new analysis
    """
    # Check if we have at least one source
    if not resume_file and not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either resume_file or resume_id must be provided"
        )
    
    # Get resume text
    resume_text = ""
    
    if resume_id:
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
    
    elif resume_file:
        # Extract text from uploaded file
        try:
            resume_text = await parse_resume_file(resume_file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse resume file: {str(e)}"
            )
    
    # If analysis result wasn't provided, perform analysis first
    if not analysis_result:
        try:
            analysis_result = await resume_analysis_service.analyze_resume(
                resume_text=resume_text,
                job_title=job_title,
                industry=industry
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