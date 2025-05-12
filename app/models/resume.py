from datetime import datetime
from typing import Optional, ClassVar, Any
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema

# Reuse the PyObjectId from user model
class PyObjectId(str):
    """Pydantic compatible ObjectId field"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )
    
    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


class ResumeBase(BaseModel):
    """Base resume model with common fields"""
    title: str
    content: str
    file_name: Optional[str] = None
    is_primary: bool = False


class ResumeInDB(ResumeBase):
    """Resume model for database storage"""
    id: PyObjectId = Field(default_factory=lambda: ObjectId(), alias="_id")
    userId: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config: ClassVar[dict] = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class Resume(ResumeBase):
    """Resume model for API responses"""
    id: str
    userId: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config: ClassVar[dict] = {
        "from_attributes": True
    }
