from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.db.mongodb import MongoDB
from app.models.skill_gap import SkillGapAnalysisInDB, SkillGapAnalysis

class SkillGapRepository:
    collection_name = "skill_gap_analyses"
    
    @property
    def collection(self):
        return MongoDB.get_db()[self.collection_name]
    
    async def create_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> SkillGapAnalysis:
        """
        Create a new skill gap analysis
        """
        # Set the user ID
        analysis_data["userId"] = ObjectId(user_id)
        
        # Create the document in the database
        analysis_in_db = SkillGapAnalysisInDB(**analysis_data)
        result = await self.collection.insert_one(analysis_in_db.model_dump(by_alias=True))
        
        # Get the created document
        created_analysis = await self.collection.find_one({"_id": result.inserted_id})
        
        # Convert to the return model
        return self._map_to_skill_gap_analysis(created_analysis)
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[SkillGapAnalysis]:
        """
        Get a skill gap analysis by ID
        """
        analysis = await self.collection.find_one({"_id": ObjectId(analysis_id)})
        if analysis:
            return self._map_to_skill_gap_analysis(analysis)
        return None
    
    async def get_analyses_by_user_id(self, user_id: str) -> List[SkillGapAnalysis]:
        """
        Get all skill gap analyses for a user
        """
        analyses = await self.collection.find({"userId": ObjectId(user_id)}).to_list(None)
        return [self._map_to_skill_gap_analysis(analysis) for analysis in analyses]
    
    async def update_analysis(self, analysis_id: str, update_data: Dict[str, Any]) -> Optional[SkillGapAnalysis]:
        """
        Update a skill gap analysis
        """
        # Update the document
        await self.collection.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": {**update_data, "updatedAt": datetime.utcnow()}}
        )
        
        # Get the updated document
        updated_analysis = await self.collection.find_one({"_id": ObjectId(analysis_id)})
        if updated_analysis:
            return self._map_to_skill_gap_analysis(updated_analysis)
        return None
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete a skill gap analysis
        """
        result = await self.collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0
    
    def _map_to_skill_gap_analysis(self, analysis_db: Dict[str, Any]) -> SkillGapAnalysis:
        """
        Map a database document to a SkillGapAnalysis model
        """
        return SkillGapAnalysis(
            id=str(analysis_db["_id"]),
            userId=str(analysis_db["userId"]),
            job_title=analysis_db["job_title"],
            job_description=analysis_db["job_description"],
            resume_text=analysis_db["resume_text"],
            match_percentage=analysis_db["match_percentage"],
            matched_skills=analysis_db["matched_skills"],
            missing_skills=analysis_db["missing_skills"],
            project_recommendations=analysis_db["project_recommendations"],
            improvement_suggestions=analysis_db["improvement_suggestions"],
            overall_assessment=analysis_db["overall_assessment"],
            createdAt=analysis_db["createdAt"],
            job_posting_url=analysis_db.get("job_posting_url")
        ) 