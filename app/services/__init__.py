# Core services
from .auth.auth_service import AuthService
from .resume.resume_service import ResumeService
from .learning_path.learning_path_service import LearningPathService
from .skill_gap.skill_gap_service import SkillGapService

# AI services
from .resume.resume_analysis_service import ResumeAnalysisService, ResumeAnalysisOutput, ImprovedResumeOutput, SimpleImprovedResumeOutput
from .learning_path.learning_path_ai_service import LearningPathAIService
from .skill_gap.skill_gap_ai_service import SkillGapAIService

# Utility services
from .utils.file_service import FileService
from .ai.base_ai_service import BaseAIService

# Export all services
__all__ = [
    # Core services
    'AuthService',
    'ResumeService',
    'LearningPathService',
    'SkillGapService',
    
    # AI services
    'ResumeAnalysisService',
    'LearningPathAIService',
    'SkillGapAIService',
    'BaseAIService',
    
    # Utility services
    'FileService',
    
    # Output models (for backward compatibility)
    'ResumeAnalysisOutput',
    'ImprovedResumeOutput',
    'SimpleImprovedResumeOutput'
]
