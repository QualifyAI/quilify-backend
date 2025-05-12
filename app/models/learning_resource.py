from typing import Optional, ClassVar
from pydantic import BaseModel, Field


class LearningResource(BaseModel):
    """
    Model for a learning resource used in learning modules
    """
    type: str  # course, book, video, article, etc.
    name: str
    link: str
    rating: Optional[float] = None
    description: Optional[str] = None
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }
