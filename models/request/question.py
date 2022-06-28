from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

class DisplayQuestionMC(BaseModel):
    num_column: int = Field(..., description='number of column')
    spacing: int = Field(..., description='spacing')

class DisplayQuestionS(BaseModel):
    num_row: int = Field(..., description='number of row')
    separate_by: str = Field(..., description='separate by')

class DisplayQuestionIP(BaseModel):
    num_row: int = Field(..., description='number of row')

class DATA_Create_Multi_Choice_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(..., description='list answer of question')
    correct_answers: str = Field(default=None, description='correct answer of question')
    display: DisplayQuestionMC = Field(..., description='display setting of question')

class DATA_Create_Sort_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(..., description='list answer of question')
    correct_answers: List[str] = Field(..., description='correct answer of question')
    display: DisplayQuestionS = Field(..., description='display setting of question')

# class MatchingAnswer(BaseModel):
#     left: List[str] = Field(..., description='list answer in the left column')
#     right: List[str] = Field(..., description='list answer in the right column')

class DATA_Create_Matching_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(..., description='answer of question')
    answers_right: List[str] = Field(..., description='answer in the right collumn of question (for matching questions)')
    correct_answers: Dict[str, List[str]] = Field(..., description='correct answer of question')

class DATA_Create_Fill_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: str = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    question_image: str = Field(default=None, description='image of question')
    correct_answers: str = Field(..., description='correct answer of question')
    display: DisplayQuestionIP = Field(..., description='display setting of question')

class DATA_Create_Answer(BaseModel):
    answer_content: str = Field(..., description='content of answer')
    answer_image: str = Field(default=None, description='image of amswer')
