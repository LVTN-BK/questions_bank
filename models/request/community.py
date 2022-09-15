from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


#==================================================================
#=================USER_REMOVE_COMMUNITY_QUESTION===================
#==================================================================
class DATA_Remove_Community_Question(BaseModel):
    question_id: str = Field(..., description='ID of question')

#==================================================================
#===================USER_REMOVE_COMMUNITY_EXAM=====================
#==================================================================
class DATA_Remove_Community_Exam(BaseModel):
    exam_id: str = Field(..., description='ID of exam')
