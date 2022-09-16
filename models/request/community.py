from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


#==================================================================
#=================USER_REMOVE_COMMUNITY_QUESTION===================
#==================================================================
class DATA_Remove_Community_Question(BaseModel):
    question_ids: List[str] = Field(..., description='List ID of question')

#==================================================================
#===================USER_REMOVE_COMMUNITY_EXAM=====================
#==================================================================
class DATA_Remove_Community_Exam(BaseModel):
    exam_ids: List[str] = Field(..., description='List ID of exam')
