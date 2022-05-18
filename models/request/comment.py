from datetime import datetime
from pydantic import BaseModel, Field


class DATA_Create_Comment(BaseModel):
    target_id: str = Field(..., description='ID of target')
    target_type: str = Field(..., description='type of target', regex='^(question|exam)$')
    content: str = Field(..., description='content of comment')

class DATA_Remove_Comment(BaseModel):
    comment_id: str = Field(..., description='ID of comment')
