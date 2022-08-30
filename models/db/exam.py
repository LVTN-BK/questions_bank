from datetime import datetime
from typing import Dict, List, Tuple, Union
from pydantic import BaseModel, Field

from models.request.exam import SectionQuestion


class Exams_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    tag_id: List[str] = Field(default=[], description='ID of tag')
    # level_id: str = Field(default=None, description='ID of level of question')
    is_public: bool = Field(default=False, description='ID of tag')
    is_removed: bool = Field(default=False, description='is removed?')
    datetime_created: float = Field(..., description='time create question')
    datetime_updated: float = Field(default=None, description='last time update question')

class Exams_Version_DB(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
    exam_title: str = Field(..., description='title of exam')
    version_name: int = Field(default=1, description='name of version')
    is_latest: bool = Field(default=True, description='is the newest version of question')
    note: str = Field(default=None, description='content of question')
    time_limit: str = Field(..., description='limit time of exam')
    organization_info: str = Field(default=None, description='organization information')
    exam_info: str = Field(default=None, description='exam information')
    questions: List[SectionQuestion] = Field(..., description='questions of exam')
    datetime_created: float = Field(..., description='time create question version')
