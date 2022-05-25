from datetime import datetime
from typing import Dict, List, Tuple, Union
from pydantic import BaseModel, Field

from models.request.exam import SectionQuestion


class Exams_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    tag_id: str = Field(default=None, description='ID of tag')
    # level_id: str = Field(default=None, description='ID of level of question')
    is_public: bool = Field(default=False, description='ID of tag')
    # liked: List[str] = Field(default=[], description='ID of tag')
    is_removed: bool = Field(default=False, description='is removed?')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create question')
    datetime_updated: float = Field(default=None, description='last time update question')

class Exams_Version_DB(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
    exam_title: str = Field(..., description='title of exam')
    is_latest: bool = Field(default=True, description='is the newest version of question')
    note: str = Field(default=None, description='content of question')
    time_limit: str = Field(..., description='limit time of exam')
    questions: List[SectionQuestion] = Field(..., description='questions of exam')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create question version')
