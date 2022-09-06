from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class CommunityQuestion(BaseModel):
    question_id: str = Field(...)
    sharer_id: str = Field(...)
    subject_id: str = Field(default=None, description='ID of subject')
    class_id: str = Field(default=None, description='ID of class')
    chapter_id: str = Field(default=None, description='ID of chapter')
    datetime_created: float= Field(...)

class CommunityExam(BaseModel):
    exam_id: str = Field(...)
    sharer_id: str = Field(...)
    subject_id: str = Field(..., description='ID of subject')
    class_id: str = Field(..., description='ID of class')
    datetime_created: float= Field(...)

