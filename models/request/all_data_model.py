from typing import Optional

from pydantic import BaseModel, Field

class DATA_Auto_comment(BaseModel):
    message: str = Field(..., description='#')
    num: Optional[int] = Field(
        default=None, description='#'
    )