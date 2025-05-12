from typing import Optional, List
from pydantic import BaseModel


class ResumeCreate(BaseModel):
    """Schema for creating a new resume"""
    title: str
    content: str
    file_name: Optional[str] = None
    is_primary: bool = False


class ResumeUpdate(BaseModel):
    """Schema for updating an existing resume"""
    title: Optional[str] = None
    content: Optional[str] = None
    file_name: Optional[str] = None
    is_primary: Optional[bool] = None


class ResumeResponse(BaseModel):
    """Schema for resume API responses"""
    id: str
    title: str
    content: str
    file_name: Optional[str] = None
    is_primary: bool
    created_at: str
    updated_at: Optional[str] = None


class ResumeListResponse(BaseModel):
    """Schema for listing multiple resumes"""
    resumes: List[ResumeResponse]
    total: int
