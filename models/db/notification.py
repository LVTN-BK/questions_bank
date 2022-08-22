from datetime import datetime
from typing import Dict, List, Tuple, Union
from pydantic import BaseModel, Field

from models.request.notification import TargetData



class Notification_DB(BaseModel):
    sender_id: str = Field(..., description='ID of sender')
    receiver_ids: List[str] = Field(..., description='List ID of receiver')
    noti_type: str = Field(..., description='Type of notification')
    content: str = Field(..., description='content')
    target: TargetData = Field(..., description='Target meta_data for create link relative')
    seen_ids: List[str] = Field(default=[], description='List ID of viewers')
    removed_ids: List[str] = Field(default=[], description='List ID of removed')
    datetime_created: float = Field(..., description='time create question')