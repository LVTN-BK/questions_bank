from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from models.request.question import DATA_Auto_Pick_Question, DATA_Evaluate_Question, Tag


class SectionQuestion(BaseModel):
    section_name: str = Field(..., description='name of section')
    section_questions: List[str] = Field(..., description='list questions of section')

class DATA_Create_Exam(BaseModel):
    num_version: int = Field(default=1, description='Number of version')
    exam_codes: List[str] = Field(default=[], description='List of exam code')
    subject_id: str = Field(..., description='ID of subject')
    class_id: str = Field(..., description='ID of class')
    tag_id: List[Tag] = Field(default=[], description='ID of tag')
    exam_title: str = Field(..., description='title of exam')
    note: str = Field(default=None, description='note of question')
    time_limit: str = Field(default=None, description='limit time of exam')
    organization_info: str = Field(default=None, description='organization information')
    exam_info: str = Field(default=None, description='exam information')
    questions: List[SectionQuestion] = Field(..., description='questions of exam')

class DATA_Update_Exam(BaseModel):
    new_version: bool = Field(default=False, description='Create new version of exam')
    exam_version_id: str = Field(..., description='ID of exam version')
    subject_id: str = Field(default=None, description='ID of subject')
    class_id: str = Field(default=None, description='ID of class')
    tag_id: List[Tag] = Field(default=[], description='ID of tag')
    exam_title: str = Field(default=None, description='title of exam')
    exam_code: str = Field(default=None, description='Exam code')
    note: str = Field(default=None, description='note of question')
    time_limit: str = Field(default=None, description='limit time of exam')
    organization_info: str = Field(default=None, description='organization information')
    exam_info: str = Field(default=None, description='exam information')
    questions: List[SectionQuestion] = Field(default=None, description='questions of exam')


class DATA_Delete_Exam(BaseModel):
    list_exam_ids: List[str] = Field(..., description='List ID of exam')


class DATA_Share_Exam_To_Group(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
    group_id: str = Field(..., description='ID of group')
    subject_id: str = Field(default=None, description='ID of subject')
    class_id: str = Field(default=None, description='ID of class')


class DATA_Share_Exam_To_Community(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
    subject_id: str = Field(default=None, description='ID of subject')
    class_id: str = Field(default=None, description='ID of class')

class DATA_Evaluate_Exam(BaseModel):
    data: List[DATA_Evaluate_Question] = Field(..., description='data to evaluate exam')


class DATA_Copy_Exam(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
    subject_id: str = Field(..., description='ID of subject')
    class_id: str = Field(..., description='ID of class')

class DATA_Copy_Exam_By_Version(BaseModel):
    exam_version_id: str = Field(..., description='ID of exam version')
    subject_id: str = Field(..., description='ID of subject')
    class_id: str = Field(..., description='ID of class')

class SaveExamConfig(BaseModel):
    section_name: str = Field(..., description='Name of section')
    section_questions: List[DATA_Auto_Pick_Question] = Field(..., description='Section questions')

class DATA_Save_Exam_Config(BaseModel):
    name: str = Field(..., description='Name of config')
    data: List[SaveExamConfig] = Field(..., description='Section questions')


class DATA_Create_New_Exam_Code(BaseModel):
    exam_code: str = Field(..., description='Create new version of exam')
    exam_version_id: str = Field(..., description='ID of exam version')

class DATA_Delete_Exam_Version(BaseModel):
    exam_version_id: str = Field(..., description='ID of exam version')

