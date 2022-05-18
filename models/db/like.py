from datetime import datetime
from typing import Dict, List, Tuple, Union
from pydantic import BaseModel, Field


class Likes_DB(BaseModel):
    user_id: str = Field(..., description='ID of user')
    target_id: str = Field(..., description='ID of target')
    target_type: str = Field(..., description='type of target', regex='^(question|exam)$')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create like')