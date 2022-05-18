from datetime import datetime
from pydantic import BaseModel, Field


class Comments_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    target_id: str = Field(..., description='ID of target')
    target_type: str = Field(..., description='type of target', regex='^(question|exam)$')
    content: str = Field(..., description='content of comment')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create like')
    datetime_created: float = Field(default=None, description='last time update comment')

class Reply_Comments_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    comment_id: str = Field(..., description='ID of comment')
    content: str = Field(..., description='content of comment')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create like')
    datetime_created: float = Field(default=None, description='last time update comment')