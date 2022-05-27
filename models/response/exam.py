#  Copyright (c) 2021.
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field



#=========================================================================
#=========================USER_GET_ONE_EXAM===============================
#=========================================================================
class AnswerInfo(BaseModel):
    answer_id: str= Field(default=None, description='ID of answer')
    answer_image: str= Field(default=None, description='image of answer')
    answer_content: str= Field(default=None, description='content of answer')
    datetime_created: str= Field(default=None, description='time create answer')

class QuestionInfo(BaseModel):
    question_id: str = Field(default=None, description='ID of question')
    question_content: str = Field(default=None, description='content of question')
    question_image: str = Field(default=None, description='image of question')
    question_type: str = Field(default=None, description='type of question', regex="^(multi_choice|sort|matching|fill)$")
    answers: List[AnswerInfo] = Field(default=None, description='list answer infomation')
    answers_right: List[AnswerInfo] = Field(default=None, description='list answer infomation (for matching questions)')
    correct_answers: str = Field(default=None, description='correct answer')
    datetime_created: float = Field(default=None, description='time create question')
    question_version_id: str = Field(default=None, description='ID of version of question')

class SectionInfo(BaseModel):
    section_name: str = Field(default=None, description='name of section')
    section_questions: List[QuestionInfo] = Field(default=None, description='list question infomation') 

class ExamInfo(BaseModel):
    user_id: str = Field(default=None, description='user who create exam')
    class_id: str = Field(default=None, description='ID of class')
    subject_id: str = Field(default=None, description='ID of subject')
    tag_id: str = Field(default=None, description='ID of tag')
    exam_id: str = Field(default=None, description='ID of exam')
    exam_title: str = Field(default=None, description='title of exam')
    note: str = Field(default=None, description='note of exam')
    time_limit: str = Field(default=None, description='time limit of exam') 
    questions: List[SectionInfo] = Field(default=None, description='list section infomation') 

class UserGetOneExamResponse200(BaseModel):
    status: str = Field(default='success', description='status of response')
    data: ExamInfo = Field(default=None, description='data of response')

class UserGetOneExamResponse403(BaseModel):
    status: str = Field(default='Failed', description='status of response')
