from fastapi import UploadFile, HTTPException, status
from typing import Optional
import io

from app.utils.resume_parser import parse_resume_file

class FileService:
    """
    Service for handling file operations like uploads, parsing, etc.
    """
    
    async def parse_resume_file(self, file: UploadFile) -> str:
        """
        Parse a resume file using the resume parser utility
        
        Args:
            file: The uploaded file to parse
            
        Returns:
            The extracted text content
        """
        try:
            return await parse_resume_file(file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse resume file: {str(e)}"
            )
    
    async def validate_file(self, file: UploadFile, allowed_extensions: list, max_size_mb: int = 5) -> bool:
        """
        Validate a file's type and size
        
        Args:
            file: The uploaded file to validate
            allowed_extensions: List of allowed file extensions (e.g., ['pdf', 'docx'])
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            True if the file is valid, raises HTTPException otherwise
        """
        # Validate file extension
        file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file_extension}. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size
        content = await file.read()
        max_size_bytes = max_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            await file.seek(0)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        return True 