from typing import Dict, List, Any, Optional
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.db.repositories.learning_path_repository import LearningPathRepository
from app.models.learning_path import (
    LearningPath, 
    Niche, 
    PathQuestion, 
    LearningPathStats,
    ModuleProgressUpdate,
    ResourceProgressUpdate,
    CustomResourceAdd,
    LearningResourceProgress
)
from app.schemas.learning_path import LearningPathRequest, LearningPathOutput
from app.services.learning_path.learning_path_ai_service import LearningPathAIService

class LearningPathService:
    """Service for managing learning path operations"""
    
    def __init__(self):
        self.repository = LearningPathRepository()
        self.ai_service = LearningPathAIService()
        
        # Cache for niches and questions to avoid repeated computation
        self._niches_cache = None
        self._questions_cache = {}
    
    async def get_all_niches(self) -> List[Niche]:
        """
        Get all available niches for learning paths
        
        Returns:
            List of Niche objects
        """
        if self._niches_cache is None:
            # Static niches for now - could be moved to database later
            self._niches_cache = [
                Niche(id=1, name="Frontend Development", icon="🎨", 
                     description="Build responsive and interactive web interfaces"),
                Niche(id=2, name="Backend Development", icon="⚙️", 
                     description="Create robust server-side applications and APIs"),
                Niche(id=3, name="Full Stack Development", icon="🔧", 
                     description="Master both frontend and backend technologies"),
                Niche(id=4, name="Mobile App Development", icon="📱", 
                     description="Develop native and cross-platform mobile applications"),
                Niche(id=5, name="Data Science", icon="📊", 
                     description="Extract insights from data using statistical analysis"),
                Niche(id=6, name="Machine Learning", icon="🤖", 
                     description="Build intelligent systems that learn from data"),
                Niche(id=7, name="DevOps", icon="🚀", 
                     description="Streamline development and deployment processes"),
                Niche(id=8, name="Cybersecurity", icon="🔒", 
                     description="Protect systems and data from digital threats"),
                Niche(id=9, name="Cloud Computing", icon="☁️", 
                     description="Design and manage scalable cloud infrastructure"),
                Niche(id=10, name="Game Development", icon="🎮", 
                     description="Create engaging games for various platforms"),
                Niche(id=11, name="UI/UX Design", icon="🎯", 
                     description="Design intuitive and user-friendly experiences"),
                Niche(id=12, name="Blockchain Development", icon="⛓️", 
                     description="Build decentralized applications and smart contracts"),
                Niche(id=13, name="AI/Artificial Intelligence", icon="🧠", 
                     description="Develop intelligent systems and neural networks"),
                Niche(id=14, name="Quality Assurance", icon="✅", 
                     description="Ensure software quality through testing and automation"),
                Niche(id=15, name="Product Management", icon="📋", 
                     description="Guide product development from concept to launch")
            ]
        
        return self._niches_cache
    
    async def get_questions_for_niche(self, niche_id: int, use_ai: bool = True) -> List[PathQuestion]:
        """
        Get questions for customizing a learning path based on niche
        
        Args:
            niche_id: ID of the selected niche
            use_ai: Whether to use AI to generate questions (default: True)
            
        Returns:
            List of PathQuestion objects
        """
        # Check cache first
        cache_key = f"{niche_id}_{use_ai}"
        if cache_key in self._questions_cache:
            return self._questions_cache[cache_key]
        
        # Get niche information
        niches = await self.get_all_niches()
        niche = next((n for n in niches if n.id == niche_id), None)
        
        if not niche:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Niche with ID {niche_id} not found"
            )
        
        if use_ai:
            questions = await self._generate_questions_with_ai(niche)
        else:
            questions = self._get_static_questions_for_niche(niche_id)
        
        # Cache the results
        self._questions_cache[cache_key] = questions
        return questions
    
    async def generate_learning_path(self, request: LearningPathRequest) -> LearningPathOutput:
        """
        Generate a learning path using AI based on user's niche and answers
        
        Args:
            request: LearningPathRequest containing niche and answers
            
        Returns:
            LearningPathOutput with generated path
        """
        # Get niche information
        niches = await self.get_all_niches()
        niche = next((n for n in niches if n.id == request.nicheId), None)
        
        if not niche:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Niche with ID {request.nicheId} not found"
            )
        
        niche_name = request.customNiche if request.customNiche else niche.name
        
        # Generate the learning path using AI
        learning_path = await self.ai_service.generate_learning_path(
            niche_name, 
            request.answers
        )
        
        return learning_path
    
    async def save_learning_path(self, user_id: str, path_data: Dict[str, Any]) -> LearningPath:
        """
        Save a learning path to the database
        
        Args:
            user_id: ID of the user
            path_data: Dictionary containing learning path data
            
        Returns:
            Saved LearningPath object
        """
        return await self.repository.create_path(user_id, path_data)
    
    async def get_user_learning_paths(self, user_id: str) -> List[LearningPath]:
        """
        Get all learning paths for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of LearningPath objects
        """
        return await self.repository.get_paths_by_user_id(user_id)
    
    async def get_learning_path(self, path_id: str) -> LearningPath:
        """
        Get a specific learning path
        
        Args:
            path_id: ID of the learning path
            
        Returns:
            LearningPath object
            
        Raises:
            HTTPException: If learning path is not found
        """
        learning_path = await self.repository.get_path_by_id(path_id)
        
        if not learning_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
            
        return learning_path
    
    async def update_learning_path(self, path_id: str, update_data: Dict[str, Any]) -> LearningPath:
        """
        Update a learning path
        
        Args:
            path_id: ID of the learning path
            update_data: Dictionary of fields to update
            
        Returns:
            Updated LearningPath object
            
        Raises:
            HTTPException: If learning path is not found
        """
        updated_path = await self.repository.update_path(path_id, update_data)
        
        if not updated_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning path with ID {path_id} not found"
            )
            
        return updated_path
    
    async def delete_learning_path(self, path_id: str) -> bool:
        """
        Delete a learning path
        
        Args:
            path_id: ID of the learning path
            
        Returns:
            True if deleted successfully, False otherwise
        """
        return await self.repository.delete_path(path_id)
    
    # New Progress Tracking Methods
    
    async def update_module_progress(self, path_id: str, progress_update: ModuleProgressUpdate) -> LearningPath:
        """
        Update progress for a specific module
        
        Args:
            path_id: ID of the learning path
            progress_update: ModuleProgressUpdate with new progress data
            
        Returns:
            Updated LearningPath object
        """
        # Get current learning path
        learning_path = await self.get_learning_path(path_id)
        
        # Find the module to update
        module_found = False
        for module in learning_path.modules:
            if module.id == progress_update.module_id:
                module_found = True
                
                # Update module fields if provided
                if progress_update.completed is not None:
                    module.completed = progress_update.completed
                    if progress_update.completed and not module.completed_at:
                        module.completed_at = datetime.utcnow()
                    elif not progress_update.completed:
                        module.completed_at = None
                
                if progress_update.progress is not None:
                    module.progress = max(0, min(100, progress_update.progress))  # Clamp between 0-100
                    
                    # Auto-set started_at if progress > 0 and not set
                    if module.progress > 0 and not module.started_at:
                        module.started_at = datetime.utcnow()
                
                if progress_update.notes is not None:
                    module.notes = progress_update.notes
                
                if progress_update.target_completion_date is not None:
                    module.target_completion_date = progress_update.target_completion_date
                
                break
        
        if not module_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module with ID {progress_update.module_id} not found in this learning path"
            )
        
        # Update the learning path in database
        update_data = {
            "modules": [module.model_dump() for module in learning_path.modules],
            "updatedAt": datetime.utcnow(),
            "last_accessed": datetime.utcnow()
        }
        
        return await self.repository.update_path(path_id, update_data)
    
    async def update_resource_progress(self, path_id: str, progress_update: ResourceProgressUpdate) -> LearningPath:
        """
        Update progress for a specific resource within a module
        
        Args:
            path_id: ID of the learning path
            progress_update: ResourceProgressUpdate with new progress data
            
        Returns:
            Updated LearningPath object
        """
        # Get current learning path
        learning_path = await self.get_learning_path(path_id)
        
        # Find the module and resource to update
        module_found = False
        resource_found = False
        
        for module in learning_path.modules:
            if module.id == progress_update.module_id:
                module_found = True
                
                # Initialize resource_progress if not exists
                if not module.resource_progress:
                    module.resource_progress = []
                
                # Find existing resource progress or create new one
                resource_progress = None
                for rp in module.resource_progress:
                    if rp.resource_id == progress_update.resource_id:
                        resource_progress = rp
                        resource_found = True
                        break
                
                if not resource_progress:
                    # Create new resource progress
                    resource_progress = LearningResourceProgress(
                        resource_id=progress_update.resource_id
                    )
                    module.resource_progress.append(resource_progress)
                
                # Update resource progress fields
                if progress_update.completed is not None:
                    resource_progress.completed = progress_update.completed
                    if progress_update.completed:
                        resource_progress.completed_at = datetime.utcnow()
                    else:
                        resource_progress.completed_at = None
                
                if progress_update.notes is not None:
                    resource_progress.notes = progress_update.notes
                
                if progress_update.rating is not None:
                    resource_progress.rating = max(1, min(5, progress_update.rating))  # Clamp between 1-5
                
                if progress_update.time_spent_minutes is not None:
                    resource_progress.time_spent_minutes = max(0, progress_update.time_spent_minutes)
                
                # Update module progress based on completed resources
                completed_resources = sum(1 for rp in module.resource_progress if rp.completed)
                total_resources = len(module.resources) + len(module.custom_resources or [])
                if total_resources > 0:
                    module.progress = (completed_resources / total_resources) * 100
                    
                    # Auto-mark module as completed if all resources are done
                    if completed_resources == total_resources:
                        module.completed = True
                        if not module.completed_at:
                            module.completed_at = datetime.utcnow()
                
                break
        
        if not module_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module with ID {progress_update.module_id} not found in this learning path"
            )
        
        # Update the learning path in database
        update_data = {
            "modules": [module.model_dump() for module in learning_path.modules],
            "updatedAt": datetime.utcnow(),
            "last_accessed": datetime.utcnow()
        }
        
        return await self.repository.update_path(path_id, update_data)
    
    async def add_custom_resource(self, path_id: str, custom_resource: CustomResourceAdd) -> LearningPath:
        """
        Add a custom resource to a module
        
        Args:
            path_id: ID of the learning path
            custom_resource: CustomResourceAdd with resource data
            
        Returns:
            Updated LearningPath object
        """
        # Get current learning path
        learning_path = await self.get_learning_path(path_id)
        
        # Find the module to add resource to
        module_found = False
        for module in learning_path.modules:
            if module.id == custom_resource.module_id:
                module_found = True
                
                # Initialize custom_resources if not exists
                if not module.custom_resources:
                    module.custom_resources = []
                
                # Add the custom resource
                module.custom_resources.append(custom_resource.resource)
                break
        
        if not module_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module with ID {custom_resource.module_id} not found in this learning path"
            )
        
        # Update the learning path in database
        update_data = {
            "modules": [module.model_dump() for module in learning_path.modules],
            "updatedAt": datetime.utcnow()
        }
        
        return await self.repository.update_path(path_id, update_data)
    
    async def calculate_path_stats(self, path_id: str) -> LearningPathStats:
        """
        Calculate comprehensive statistics for a learning path
        
        Args:
            path_id: ID of the learning path
            
        Returns:
            LearningPathStats object with calculated statistics
        """
        learning_path = await self.get_learning_path(path_id)
        
        stats = LearningPathStats()
        
        # Basic counts
        stats.total_modules = len(learning_path.modules)
        stats.completed_modules = sum(1 for module in learning_path.modules if module.completed)
        
        # Resource counts
        total_resources = 0
        completed_resources = 0
        total_time_spent = 0
        completion_dates = []
        
        for module in learning_path.modules:
            # Count original and custom resources
            module_resources = len(module.resources)
            if module.custom_resources:
                module_resources += len(module.custom_resources)
            
            total_resources += module_resources
            
            # Count completed resources and time spent
            if module.resource_progress:
                for rp in module.resource_progress:
                    if rp.completed:
                        completed_resources += 1
                    if rp.time_spent_minutes:
                        total_time_spent += rp.time_spent_minutes
            
            # Collect completion dates for analysis
            if module.completed_at:
                completion_dates.append(module.completed_at)
        
        stats.total_resources = total_resources
        stats.completed_resources = completed_resources
        stats.total_time_spent_minutes = total_time_spent
        
        # Calculate average completion time
        if len(completion_dates) > 1:
            start_dates = [module.started_at for module in learning_path.modules if module.started_at]
            if start_dates:
                total_days = 0
                count = 0
                for i, completion_date in enumerate(completion_dates):
                    if i < len(start_dates):
                        days_diff = (completion_date - start_dates[i]).days
                        if days_diff > 0:
                            total_days += days_diff
                            count += 1
                
                if count > 0:
                    stats.average_module_completion_days = total_days / count
        
        # Estimate completion date based on current progress
        if stats.completed_modules < stats.total_modules:
            remaining_modules = stats.total_modules - stats.completed_modules
            
            if stats.average_module_completion_days:
                estimated_days = remaining_modules * stats.average_module_completion_days
                stats.estimated_completion_date = datetime.utcnow() + timedelta(days=estimated_days)
            else:
                # Default estimate if no historical data
                stats.estimated_completion_date = datetime.utcnow() + timedelta(days=remaining_modules * 14)  # 2 weeks per module
        
        # Last activity date
        last_activities = []
        if learning_path.last_accessed:
            last_activities.append(learning_path.last_accessed)
        
        for module in learning_path.modules:
            if module.completed_at:
                last_activities.append(module.completed_at)
            if module.resource_progress:
                for rp in module.resource_progress:
                    if rp.completed_at:
                        last_activities.append(rp.completed_at)
        
        if last_activities:
            stats.last_activity_date = max(last_activities)
        
        return stats
    
    async def update_path_notes(self, path_id: str, notes: str) -> None:
        """
        Update custom notes for a learning path
        
        Args:
            path_id: ID of the learning path
            notes: New notes content
        """
        await self.repository.update_path(path_id, {
            "custom_notes": notes,
            "updatedAt": datetime.utcnow()
        })
    
    async def update_target_completion_date(self, path_id: str, target_date: datetime) -> None:
        """
        Update target completion date for a learning path
        
        Args:
            path_id: ID of the learning path
            target_date: New target completion date
        """
        await self.repository.update_path(path_id, {
            "target_completion_date": target_date,
            "updatedAt": datetime.utcnow()
        })
    
    # Helper methods for generating questions and paths
    
    async def _generate_questions_with_ai(self, niche: Niche) -> List[PathQuestion]:
        """Generate customization questions using AI"""
        # Use AI to generate personalized questions based on niche
        return await self.ai_service.generate_questions_for_niche(niche.name)
    
    def _get_static_questions_for_niche(self, niche_id: int) -> List[PathQuestion]:
        """Get static questions for a niche (fallback when AI is disabled)"""
        # This could be expanded with niche-specific questions
        base_questions = [
            PathQuestion(
                id=f"static_{niche_id}_1",
                label="What is your current experience level?",
                options=["Complete Beginner", "Some Experience", "Intermediate", "Advanced"]
            ),
            PathQuestion(
                id=f"static_{niche_id}_2",
                label="How much time can you dedicate per week?",
                options=["1-5 hours", "5-10 hours", "10-20 hours", "20+ hours"]
            ),
            PathQuestion(
                id=f"static_{niche_id}_3",
                label="What is your preferred learning style?",
                options=["Video Tutorials", "Reading Documentation", "Hands-on Projects", "Interactive Courses"]
            )
        ]
        
        return base_questions 