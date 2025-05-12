from typing import Dict, List, Optional, Any
from fastapi import UploadFile, HTTPException, status

from app.db.repositories.resume_repository import ResumeRepository
from app.models.resume import Resume
from app.utils.resume_parser import parse_resume_file


class ResumeService:
    def __init__(self):
        self.repository = ResumeRepository()
    
    async def upload_resume(
        self,
        user_id: str,
        title: str,
        file: UploadFile,
        is_primary: bool = False
    ) -> Resume:
        """
        Upload and process a new resume file
        """
        # Extract text from the resume file
        resume_text = await parse_resume_file(file)
        
        # Prepare data for saving
        resume_data = {
            "title": title,
            "content": resume_text,
            "file_name": file.filename,
            "is_primary": is_primary
        }
        
        # Save to database
        return await self.repository.create_resume(user_id, resume_data)
    
    async def save_resume_text(
        self,
        user_id: str,
        title: str,
        content: str,
        is_primary: bool = False
    ) -> Resume:
        """
        Save resume text directly without file upload
        """
        resume_data = {
            "title": title,
            "content": content,
            "is_primary": is_primary
        }
        
        return await self.repository.create_resume(user_id, resume_data)
    
    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """
        Get a resume by ID
        """
        resume = await self.repository.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found"
            )
        return resume
    
    async def get_user_resumes(self, user_id: str) -> List[Resume]:
        """
        Get all resumes for a user
        """
        return await self.repository.get_resume_by_user_id(user_id)
    
    async def get_primary_resume(self, user_id: str) -> Optional[Resume]:
        """
        Get the primary resume for a user
        """
        return await self.repository.get_primary_resume(user_id)
    
    async def update_resume(self, resume_id: str, update_data: Dict[str, Any]) -> Resume:
        """
        Update a resume
        """
        resume = await self.repository.update_resume(resume_id, update_data)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found"
            )
        return resume
    
    async def delete_resume(self, resume_id: str) -> bool:
        """
        Delete a resume
        """
        # Get the resume first to check if it exists
        resume = await self.repository.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found"
            )
            
        return await self.repository.delete_resume(resume_id)
    
    async def set_primary_resume(self, user_id: str, resume_id: str) -> Resume:
        """
        Set a resume as the primary resume for a user
        """
        # Check if the resume exists
        resume = await self.repository.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found"
            )
            
        # Check if the resume belongs to the user
        if resume.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: The resume does not belong to the current user"
            )
            
        # Update the resume to be primary
        return await self.repository.update_resume(resume_id, {"is_primary": True})
