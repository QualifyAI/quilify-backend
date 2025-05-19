from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.db.mongodb import MongoDB
from app.services.resume.models import ResumeAnalysisOutput

class ResumeAnalysisRepository:
    collection_name = "resume_analyses"
    
    @property
    def collection(self):
        return MongoDB.get_db()[self.collection_name]
    
    async def save_analysis(self, user_id: str, resume_id: str, analysis_data: Dict[str, Any]) -> str:
        """
        Save resume analysis result to database
        
        Args:
            user_id: ID of the user who owns the analysis
            resume_id: ID of the resume that was analyzed
            analysis_data: Analysis result data
            
        Returns:
            ID of the saved analysis
        """
        # Add metadata
        document = {
            "userId": ObjectId(user_id),
            "resumeId": ObjectId(resume_id),
            "createdAt": datetime.utcnow(),
            "analysisData": analysis_data
        }
        
        # Insert into database
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[ResumeAnalysisOutput]:
        """
        Get analysis by ID
        
        Args:
            analysis_id: ID of the analysis to retrieve
            
        Returns:
            ResumeAnalysisOutput if found, None otherwise
        """
        if not ObjectId.is_valid(analysis_id):
            return None
            
        document = await self.collection.find_one({"_id": ObjectId(analysis_id)})
        if not document:
            return None
            
        # Convert from stored format to ResumeAnalysisOutput
        return ResumeAnalysisOutput.model_validate(document["analysisData"])
    
    async def get_analyses_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all analyses for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of analysis metadata (without full analysis data)
        """
        if not ObjectId.is_valid(user_id):
            return []
            
        cursor = self.collection.find(
            {"userId": ObjectId(user_id)},
            # Exclude the full analysis data for performance
            {"analysisData": 0}
        )
        
        results = await cursor.to_list(length=100)
        return [
            {
                "id": str(doc["_id"]),
                "userId": str(doc["userId"]),
                "resumeId": str(doc["resumeId"]),
                "createdAt": doc["createdAt"]
            }
            for doc in results
        ]
    
    async def get_analyses_by_resume_id(self, resume_id: str) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific resume
        
        Args:
            resume_id: ID of the resume
            
        Returns:
            List of analysis metadata (without full analysis data)
        """
        if not ObjectId.is_valid(resume_id):
            return []
            
        cursor = self.collection.find(
            {"resumeId": ObjectId(resume_id)},
            # Exclude the full analysis data for performance
            {"analysisData": 0}
        )
        
        results = await cursor.to_list(length=100)
        return [
            {
                "id": str(doc["_id"]),
                "userId": str(doc["userId"]),
                "resumeId": str(doc["resumeId"]),
                "createdAt": doc["createdAt"]
            }
            for doc in results
        ]
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis
        
        Args:
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not ObjectId.is_valid(analysis_id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0 