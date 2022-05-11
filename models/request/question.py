from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class DATA_Create_Multi_Choice_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level_id: str = Field(default=None, description='ID of tag')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(default=[], description='list answer of question')
    correct_answers: str = Field(default=None, description='correct answer of question')

class DATA_Create_Sort_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level_id: str = Field(default=None, description='ID of tag')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(..., description='list answer of question')
    correct_answers: List[str] = Field(..., description='correct answer of question')

class DATA_Create_Matching_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level_id: str = Field(default=None, description='ID of tag')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: Tuple[List[str], List[str]] = Field(..., description='list answer of question')
    correct_answers: Dict[str, List[str]] = Field(..., description='correct answer of question')

class DATA_Create_Fill_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level_id: str = Field(default=None, description='ID of tag')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    correct_answers: str = Field(..., description='correct answer of question')

class DATA_Create_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    type_id: str = Field(..., description='ID of question type')
    tag_id: str = Field(default=None, description='ID of tag')
    level_id: str = Field(default=None, description='ID of tag')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: Union[List[str], Tuple[List[str], List[str]]] = Field(default=None, description='image of question')