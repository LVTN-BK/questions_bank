from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

class Tag(BaseModel):
    id: str = Field(..., description='ID of tag')
    isNew: bool = Field(..., description='tag is new?')
    name: str = Field(..., description='name of tag')

class DisplayQuestionMC(BaseModel):
    num_column: int = Field(..., description='number of column')
    spacing: int = Field(..., description='spacing')

class DisplayQuestionM(BaseModel):
    row_space: int = Field(..., description='row space')
    column_space: int = Field(..., description='column space')

class AnswerMC(BaseModel): # multichoice
    content: str = Field(..., description='content of answer')
    isCorrect: bool = Field(..., description='is correct answer')

class AnswerM(BaseModel): # matching
    content: str = Field(..., description='content of answer')
    id: str = Field(..., description='id of answer')

class DisplayQuestionS(BaseModel):
    num_row: int = Field(..., description='number of row')
    separate_by: str = Field(..., description='separate by')

class DisplayQuestionIP(BaseModel):
    num_row: int = Field(..., description='number of row')

class DATA_Create_Multi_Choice_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: List[Tag] = Field(default=[], description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(default=None, description='image of question')
    answers: List[AnswerMC] = Field(..., description='list answer of question')
    # correct_answers: str = Field(default=None, description='correct answer of question')
    display: DisplayQuestionMC = Field(..., description='display setting of question')

class DATA_Create_Sort_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: List[Tag] = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(default=None, description='image of question')
    answers: List[str] = Field(..., description='list answer of question')
    sample_answer: List[str] = Field(..., description='correct answer of question')
    display: DisplayQuestionS = Field(..., description='display setting of question')

# class MatchingAnswer(BaseModel):
#     left: List[str] = Field(..., description='list answer in the left column')
#     right: List[str] = Field(..., description='list answer in the right column')

class DATA_Create_Matching_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: List[Tag] = Field(default=None, description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(default=None, description='image of question')
    answers: List[AnswerM] = Field(..., description='answer of question')
    answers_right: List[AnswerM] = Field(..., description='answer in the right collumn of question (for matching questions)')
    # sample_answer: Dict[str, List[str]] = Field(..., description='correct answer of question')
    sample_answer: List[Tuple[str, str]] = Field(..., description='correct answer of question')
    display: DisplayQuestionM = Field(..., description='display setting of question')

class DATA_Create_Fill_Question(BaseModel):
    class_id: str = Field(..., description='ID of class')
    subject_id: str = Field(..., description='ID of subject')
    chapter_id: str = Field(..., description='ID of chapter')
    tag_id: List[Tag] = Field(default=[], description='ID of tag')
    level: str = Field(default=None, description='level of question')
    question_content: str = Field(..., description='content of question')
    # question_image: str = Field(default=None, description='image of question')
    sample_answer: str = Field(..., description='correct answer of question')
    display: DisplayQuestionIP = Field(..., description='display setting of question')

class DATA_Create_Answer(BaseModel):
    answer_content: str = Field(..., description='content of answer')
    answer_image: str = Field(default=None, description='image of amswer')


class DATA_Delete_Question(BaseModel):
    list_question_ids: List[str] = Field(..., description='List ID of question')


class DATA_Share_Question_To_Community(BaseModel):
    question_id: str = Field(..., description='ID of question')


class DATA_Share_Question_To_Group(BaseModel):
    question_id: str = Field(..., description='ID of question')
    group_id: str = Field(..., description='ID of group')
