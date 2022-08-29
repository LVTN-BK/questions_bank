from datetime import datetime
from pydantic import BaseModel, Field


class DATA_Create_Subject(BaseModel):
    name: str = Field(..., description='name of subject')

class DATA_Group_Create_Subject(BaseModel):
    name: str = Field(..., description='name of subject')
    group_id: str = Field(..., description='ID of group')

class DATA_Update_Subject(BaseModel):
    subject_id: str = Field(..., description='ID of subject')
    name: str = Field(..., description='name of subject')

class DATA_Delete_Subject(BaseModel):
    subject_id: str = Field(..., description='ID of subject')

class DATA_Create_Class(BaseModel):
    name: str = Field(..., description='name of class')
    subject_id: str = Field(..., description='ID of subject')

class DATA_Update_class(BaseModel):
    class_id: str = Field(..., description='ID of class')
    name: str = Field(..., description='name of class')

class DATA_Delete_Class(BaseModel):
    class_id: str = Field(..., description='ID of class')

class DATA_Create_Chapter(BaseModel):
    name: str = Field(..., description='name of chapter')
    class_id: str = Field(..., description='ID of class')


class DATA_Update_chapter(BaseModel):
    chapter_id: str = Field(..., description='ID of chapter')
    name: str = Field(..., description='name of chapter')

class DATA_Delete_Chapter(BaseModel):
    chapter_id: str = Field(..., description='ID of chapter')
