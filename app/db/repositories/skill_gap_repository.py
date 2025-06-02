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
        # Set the user ID - store as string to match resume collection
        print(f"Creating analysis for user: {user_id}")
        analysis_data["userId"] = user_id
        
        # Add creation timestamp
        analysis_data["createdAt"] = datetime.utcnow()
        
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
    
    async def find_by_user_id_flexible(self, user_id: str):
        """
        Utility method to find documents by user ID, trying different ID formats
        """
        results = []
        
        # Try as ObjectId first
        try:
            print(f"Trying to find analyses with userId as ObjectId: {user_id}")
            cursor = self.collection.find({"userId": ObjectId(user_id)})
            obj_id_results = await cursor.to_list(None)
            if obj_id_results:
                print(f"Found {len(obj_id_results)} analyses with ObjectId")
                results.extend(obj_id_results)
        except Exception as e:
            print(f"ObjectId search failed: {e}")
        
        # Try as string
        if not results:
            try:
                print(f"Trying to find analyses with userId as string: {user_id}")
                cursor = self.collection.find({"userId": user_id})
                string_results = await cursor.to_list(None)
                if string_results:
                    print(f"Found {len(string_results)} analyses with string ID")
                    results.extend(string_results)
            except Exception as e:
                print(f"String ID search failed: {e}")
        
        return results
    
    async def get_analyses_by_user_id(self, user_id: str) -> List[SkillGapAnalysis]:
        """
        Get all skill gap analyses for a user
        """
        print(f"Getting all analyses for user: {user_id}")
        analyses = await self.find_by_user_id_flexible(user_id)
        if not analyses:
            print(f"No analyses found for user {user_id}")
            return []
        
        print(f"Found {len(analyses)} analyses for user {user_id}")
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
        # Handle legacy matched_skills that might be missing required fields
        matched_skills = analysis_db.get("matched_skills", [])
        for skill in matched_skills:
            if "evidence" not in skill:
                skill["evidence"] = "Evidence not available"
            if "meets_requirement" not in skill:
                skill["meets_requirement"] = True
        
        # Handle legacy missing_skills that might be missing required fields
        missing_skills = analysis_db.get("missing_skills", [])
        for skill in missing_skills:
            if "why_needed" not in skill:
                skill["why_needed"] = "Required for role"
            if "learning_path" not in skill:
                skill["learning_path"] = "Recommended to learn through courses or practice"
        
        # Handle legacy project_recommendations that might be missing required fields
        project_recommendations = analysis_db.get("project_recommendations", [])
        for project in project_recommendations:
            if "skills_gained" not in project:
                project["skills_gained"] = "Various technical skills"
            if "time_estimate" not in project:
                project["time_estimate"] = "1-3 months"
        
        return SkillGapAnalysis(
            id=str(analysis_db.get("_id")),
            userId=str(analysis_db.get("userId")),
            job_title=analysis_db.get("job_title"),
            job_description=analysis_db.get("job_description"),
            resume_text=analysis_db.get("resume_text"),
            match_percentage=analysis_db.get("match_percentage"),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            project_recommendations=project_recommendations,
            top_strengths=analysis_db.get("top_strengths") or "Not available",
            biggest_gaps=analysis_db.get("biggest_gaps") or "Not available",
            next_steps=analysis_db.get("next_steps") or "Not available",
            timeline_to_ready=analysis_db.get("timeline_to_ready") or "Not available",
            overall_assessment=analysis_db.get("overall_assessment"),
            createdAt=analysis_db.get("createdAt"),
            job_posting_url=analysis_db.get("job_posting_url")
        ) 