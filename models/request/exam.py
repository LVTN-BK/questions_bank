from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class DATA_Create_Exam(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    tag_id: str = Field(default=None, description='ID of tag')
    exam_title: str = Field(..., description='title of exam')
    note: str = Field(default=None, description='image of question')
    time_limit: str = Field(default=None, description='limit time of exam')
    questions: List[str] = Field(..., description='answer of question')
