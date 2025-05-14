from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.db.mongodb import MongoDB
from app.models.resume import ResumeInDB, Resume

class ResumeRepository:
    collection_name = "resumes"
    
    @property
    def collection(self):
        return MongoDB.get_db()[self.collection_name]
    
    async def create_resume(self, user_id: str, resume_data: Dict[str, Any]) -> Resume:
        """
        Create a new resume for a user
        """
        # If this is set as primary, unset any other primary resumes for this user
        if resume_data.get("is_primary", False):
            await self.collection.update_many(
                {"userId": ObjectId(user_id)},
                {"$set": {"is_primary": False}}
            )
        
        # Set the user ID and timestamps
        resume_data["userId"] = ObjectId(user_id)
        resume_data["created_at"] = datetime.utcnow()
        
        # Create resume in database
        resume_in_db = ResumeInDB(**resume_data)
        result = await self.collection.insert_one(resume_in_db.model_dump(by_alias=True))
        
        # Get the created document
        created_resume = await self.collection.find_one({"_id": result.inserted_id})
        
        # Convert to the return model
        return self._map_to_resume(created_resume)
    
    async def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """
        Get a resume by ID
        """
        print(f"Getting resume with ID: {resume_id}")
        resume = await self.find_by_id_flexible(resume_id)
        if resume:
            return self._map_to_resume(resume)
        return None
    
    async def get_resume_by_user_id(self, user_id: str, primary_only: bool = False) -> List[Resume]:
        """
        Get all resumes for a user
        """
        query = {"userId": ObjectId(user_id)}
        if primary_only:
            query["is_primary"] = True
        
        resumes = await self.collection.find(query).to_list(None)
        return [self._map_to_resume(resume) for resume in resumes]
    
    async def get_primary_resume(self, user_id: str) -> Optional[Resume]:
        """
        Get the primary resume for a user
        """
        resumes = await self.get_resume_by_user_id(user_id, primary_only=True)
        return resumes[0] if resumes else None
    
    async def update_resume(self, resume_id: str, update_data: Dict[str, Any]) -> Optional[Resume]:
        """
        Update a resume
        """
        # If setting as primary, unset any other primary resumes for this user
        resume = await self.collection.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            return None
            
        user_id = resume["userId"]
        
        if update_data.get("is_primary", False):
            await self.collection.update_many(
                {"userId": user_id, "_id": {"$ne": ObjectId(resume_id)}},
                {"$set": {"is_primary": False}}
            )
        
        # Set updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update the document
        await self.collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": update_data}
        )
        
        # Get the updated document
        updated_resume = await self.collection.find_one({"_id": ObjectId(resume_id)})
        if updated_resume:
            return self._map_to_resume(updated_resume)
        return None
    
    async def delete_resume(self, resume_id: str) -> bool:
        """
        Delete a resume
        """
        result = await self.collection.delete_one({"_id": ObjectId(resume_id)})
        return result.deleted_count > 0
    
    def _map_to_resume(self, resume_db: Dict[str, Any]) -> Resume:
        """
        Map a database document to a Resume model
        """
        return Resume(
            id=str(resume_db["_id"]),
            userId=str(resume_db["userId"]),
            title=resume_db["title"],
            content=resume_db["content"],
            file_name=resume_db.get("file_name"),
            is_primary=resume_db.get("is_primary", False),
            created_at=resume_db["created_at"],
            updated_at=resume_db.get("updated_at")
        )
    
    async def find_by_id_flexible(self, id_value: str):
        """
        Utility method to find a document by ID, trying different ID formats
        """
        # Try as string first since that's what's working in our database
        try:
            print(f"Trying to find with string ID: {id_value}")
            result = await self.collection.find_one({"_id": id_value})
            if result:
                print(f"Found with string ID")
                return result
        except Exception as e:
            print(f"String ID lookup failed: {e}")
        
        # Try as ObjectId
        try:
            print(f"Trying to find with ObjectId: {id_value}")
            result = await self.collection.find_one({"_id": ObjectId(id_value)})
            if result:
                print(f"Found with ObjectId")
                return result
        except Exception as e:
            print(f"ObjectId conversion failed: {e}")
        
        # Try the string ID with quotes
        try:
            print(f"Trying to find with quoted string ID: '{id_value}'")
            result = await self.collection.find_one({"_id": f"{id_value}"})
            if result:
                print(f"Found with quoted string ID")
                return result
        except Exception as e:
            print(f"Quoted string ID lookup failed: {e}")
        
        print(f"Document not found with any ID format: {id_value}")
        return None 