from datetime import datetime
from typing import Dict, List, Tuple, Union
from models.request.question import AnswerM, AnswerMC, DisplayQuestionIP, DisplayQuestionMC, DisplayQuestionS
from pydantic import BaseModel, Field


class Questions_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    type: str = Field(..., description='question type')
    tag_id: List[str] = Field(default=[], description='ID of tag')
    level: str = Field(default=None, description='level of question')
    is_public: bool = Field(default=False, description='ID of tag')
    # liked: List[str] = Field(default=[], description='ID of tag')
    is_removed: bool = Field(default=False, description='is removed?')
    datetime_created: float = Field(..., description='time create question')

class Questions_Version_DB(BaseModel):
    question_id: str = Field(..., description='ID of question')
    is_latest: bool = Field(default=True, description='is the newest version of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(..., description='image of question')
    answers: Union[List[AnswerM], List[str], List[AnswerMC]] = Field(default=[], description='answer of question')
    answers_right: List[AnswerM] = Field(default=[], description='answer right for matching question')
    sample_answer: Union[str, List[str], List[Tuple[str, str]]] = Field(default="", description='sample answer of fill question')
    # correct_answers: Union[str, List[str], Dict[str, List[str]]] = Field(..., description='correct answer of question')
    display: Union[DisplayQuestionMC, DisplayQuestionS, DisplayQuestionIP] = Field(default=None, description='question display setting')
    datetime_created: float = Field(..., description='time create question version')

class Answers_DB(BaseModel):
    answer_content: str = Field(..., description='content of answer')
    answer_image: str = Field(default=None, description='image of amswer')
    datetime_created: float = Field(..., description='time create answer')