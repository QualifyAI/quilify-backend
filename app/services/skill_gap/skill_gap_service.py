from typing import Dict, Optional
from fastapi import HTTPException, status

from app.db.repositories.skill_gap_repository import SkillGapRepository
from app.models.skill_gap import SkillGapAnalysis
from app.schemas.skill_gap import SkillGapAnalysisOutput
from .skill_gap_ai_service import SkillGapAIService

class SkillGapService:
    """Service for managing skill gap analysis operations"""
    
    def __init__(self):
        self.repository = SkillGapRepository()
        self.ai_service = SkillGapAIService()
    
    async def analyze_skill_gap(
        self, 
        user_id: str,
        resume_id: str,
        job_description: str,
        job_posting_url: Optional[str] = None
    ) -> SkillGapAnalysisOutput:
        """
        Analyze the skill gap between a user's resume and a job description
        
        Args:
            user_id: ID of the user
            resume_id: ID of the resume to analyze
            job_description: Text of the job description
            job_posting_url: Optional URL of the job posting
            
        Returns:
            SkillGapAnalysisOutput containing detailed analysis
        """
        from app.services import ResumeService
        resume_service = ResumeService()
        
        # Get the resume
        try:
            resume = await resume_service.get_resume(resume_id)
            
            # Check if resume belongs to user
            if resume.userId != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this resume"
                )
            
            # Use AI service to perform analysis
            analysis_result = await self.ai_service.analyze_skill_gap(
                resume_text=resume.content,
                job_description=job_description,
                job_posting_url=job_posting_url
            )
            
            # Store the analysis result with correct field mapping
            skill_gap_data = {
                "job_title": analysis_result.job_title,
                "job_description": job_description,
                "resume_text": resume.content,
                "match_percentage": analysis_result.match_percentage,
                "matched_skills": [skill.model_dump() for skill in analysis_result.matched_skills],
                "missing_skills": [skill.model_dump() for skill in analysis_result.missing_skills],
                "project_recommendations": [proj.model_dump() for proj in analysis_result.project_recommendations],
                "improvement_suggestions": analysis_result.improvement_suggestions,
                "overall_assessment": analysis_result.overall_assessment,
                "job_posting_url": job_posting_url
            }
            
            await self.repository.create_analysis(user_id, skill_gap_data)
            
            return analysis_result
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle other exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing skill gap: {str(e)}"
            )
    
    async def get_skill_gap_analyses(self, user_id: str) -> list[SkillGapAnalysis]:
        """
        Get all skill gap analyses for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of SkillGapAnalysis objects
        """
        return await self.repository.get_analyses_by_user_id(user_id)
    
    async def get_skill_gap_analysis(self, analysis_id: str) -> SkillGapAnalysis:
        """
        Get a specific skill gap analysis
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            SkillGapAnalysis object
            
        Raises:
            HTTPException: If analysis is not found
        """
        analysis = await self.repository.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill gap analysis with ID {analysis_id} not found"
            )
            
        return analysis
    
    async def delete_skill_gap_analysis(self, analysis_id: str) -> bool:
        """
        Delete a skill gap analysis
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If analysis is not found
        """
        analysis = await self.repository.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill gap analysis with ID {analysis_id} not found"
            )
            
        return await self.repository.delete_analysis(analysis_id)
            
    async def fetch_job_description(self, url: str) -> str:
        """
        Fetch job description from a URL
        
        Args:
            url: URL of the job posting
            
        Returns:
            The extracted job description text
        """
        return await self.ai_service.fetch_job_description(url) 