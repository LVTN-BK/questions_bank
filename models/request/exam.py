from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from models.request.question import Tag


class SectionQuestion(BaseModel):
    section_name: str = Field(..., description='name of section')
    section_questions: List[str] = Field(..., description='list questions of section')

class DATA_Create_Exam(BaseModel):
    subject_id: str = Field(..., description='ID of subject')
    class_id: str = Field(..., description='ID of class')
    tag_id: List[Tag] = Field(default=[], description='ID of tag')
    exam_title: str = Field(..., description='title of exam')
    note: str = Field(default=None, description='note of question')
    time_limit: str = Field(default=None, description='limit time of exam')
    questions: List[SectionQuestion] = Field(..., description='questions of exam')
