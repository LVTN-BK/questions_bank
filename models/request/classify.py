from datetime import datetime
from pydantic import BaseModel, Field


class DATA_Create_Subject(BaseModel):
    name: str = Field(..., description='name of subject')

class DATA_Create_Class(BaseModel):
    name: str = Field(..., description='name of class')
    subject_id: str = Field(..., description='ID of subject')

class DATA_Create_Chapter(BaseModel):
    name: str = Field(..., description='name of chapter')
    class_id: str = Field(..., description='ID of class')
