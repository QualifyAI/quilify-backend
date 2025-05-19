from typing import Dict, List, Optional, Any
from fastapi import UploadFile, HTTPException, status

from app.db.repositories.resume_repository import ResumeRepository
from app.models.resume import Resume
from app.services.utils.file_service import FileService

class ResumeService:
    """Service for managing resume operations"""
    
    def __init__(self):
        self.repository = ResumeRepository()
        self.file_service = FileService()
    
    async def upload_resume(
        self,
        user_id: str,
        title: str,
        file: UploadFile,
        is_primary: bool = False
    ) -> Resume:
        """
        Upload and process a new resume file
        
        Args:
            user_id: ID of the user who owns the resume
            title: Title of the resume
            file: Uploaded resume file
            is_primary: Whether this resume should be set as primary
            
        Returns:
            Newly created Resume object
        """
        # Extract text from the resume file
        resume_text = await self.file_service.parse_resume_file(file)
        
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
        
        Args:
            user_id: ID of the user who owns the resume
            title: Title of the resume
            content: Text content of the resume
            is_primary: Whether this resume should be set as primary
            
        Returns:
            Newly created Resume object
        """
        resume_data = {
            "title": title,
            "content": content,
            "is_primary": is_primary
        }
        
        return await self.repository.create_resume(user_id, resume_data)
    
    async def get_resume(self, resume_id: str) -> Resume:
        """
        Get a resume by ID
        
        Args:
            resume_id: ID of the resume to retrieve
            
        Returns:
            Resume object if found
            
        Raises:
            HTTPException: If resume is not found
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
        
        Args:
            user_id: ID of the user whose resumes to retrieve
            
        Returns:
            List of Resume objects
        """
        return await self.repository.get_resume_by_user_id(user_id)
    
    async def get_primary_resume(self, user_id: str) -> Optional[Resume]:
        """
        Get the primary resume for a user
        
        Args:
            user_id: ID of the user whose primary resume to retrieve
            
        Returns:
            Primary Resume object if found, None otherwise
        """
        return await self.repository.get_primary_resume(user_id)
    
    async def update_resume(self, resume_id: str, update_data: Dict[str, Any]) -> Resume:
        """
        Update a resume
        
        Args:
            resume_id: ID of the resume to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Resume object
            
        Raises:
            HTTPException: If resume is not found
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
        
        Args:
            resume_id: ID of the resume to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If resume is not found
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
        
        Args:
            user_id: ID of the user
            resume_id: ID of the resume to set as primary
            
        Returns:
            Updated Resume object
            
        Raises:
            HTTPException: If resume is not found or doesn't belong to the user
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