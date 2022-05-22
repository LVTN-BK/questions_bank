from datetime import datetime
from pydantic import BaseModel, Field


class Subjects_DB(BaseModel):
    name: str = Field(..., description='name of subject')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create subject')
    datetime_updated: float = Field(default=None, description='last time update subject')
    

class Class_DB(BaseModel):
    name: str = Field(..., description='name of class')
    subject_id: str = Field(..., description='ID of subject')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create class')
    datetime_updated: float = Field(default=None, description='last time update class')

class Chapters_DB(BaseModel):
    name: str = Field(..., description='name of chapter')
    class_id: str = Field(..., description='ID of class')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create chapter')
    datetime_updated: float = Field(default=None, description='last time update chapter')
