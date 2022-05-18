from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class DATA_Create_Like(BaseModel):
    target_id: str = Field(..., description='ID of target')
    target_type: str = Field(..., description='type of target', regex='^(question|exam)$')

class DATA_Unlike(BaseModel):
    target_id: str = Field(..., description='ID of target')
    target_type: str = Field(..., description='type of target', regex='^(question|exam)$')
