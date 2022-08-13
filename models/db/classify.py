from datetime import datetime
from pydantic import BaseModel, Field


class Subjects_DB(BaseModel):
    name: str = Field(..., description='name of subject')
    user_id: str = Field(..., description='ID of user')
    datetime_created: float = Field(..., description='time create subject')
    datetime_updated: float = Field(default=None, description='last time update subject')
    

class Class_DB(BaseModel):
    name: str = Field(..., description='name of class')
    user_id: str = Field(..., description='ID of user')
    subject_id: str = Field(..., description='ID of subject')
    datetime_created: float = Field(..., description='time create class')
    datetime_updated: float = Field(default=None, description='last time update class')

class Chapters_DB(BaseModel):
    name: str = Field(..., description='name of chapter')
    user_id: str = Field(..., description='ID of user')
    class_id: str = Field(..., description='ID of class')
    datetime_created: float = Field(..., description='time create chapter')
    datetime_updated: float = Field(default=None, description='last time update chapter')
