from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl


class TargetData(BaseModel):
    """Chat group model"""
    # user_id: str = Field(default=None, description='ID of user')
    # user_name: str = Field(default=None, description='name of user')
    group_id: str = Field(default=None, description='ID of group')
    exam_id: str = Field(default=None, description='name of group')
    question_id: str = Field(default=None, description='ID of post')
    comment_id: str = Field(default=None, description='ID of comment')

class DATA_Create_Noti_List_User(BaseModel):
    sender_id: Optional[str] = Field(default='#', description='ID of sender')
    list_users: List[str] = Field(default=[], description='list specific users will receive notification')
    noti_type: str = Field(default=None, description='type of Notification')
    target: Optional[TargetData] = Field(default=None, description='target data')
    # target_id: Optional[str] = Body(default=None, description='maybe post_id, event_id,...'),
    # target_type: Optional[str] = Body(default=None, description='maybe post_id, event_id,...')

class DATA_Create_Noti_Group_Members_Except_User(BaseModel):
    group_id: str = Field(..., description="ID of group")
    sender_id: str = Field(..., description="User ID who create the notification")
    noti_type: str = Field(default=None, description='type of notification')
    target: Optional[TargetData] = Field(default=None, description='target data')

class DATA_Update_Notification_Setting(BaseModel):
    noti_type: str = Field(..., description="type of notification")
    is_enable: bool = Field(..., description='setting status')

class DATA_Delete_Notification(BaseModel):
    noti_id: str = Field(..., description='ID of notification will be deleted by user')

class DATA_Mark_Notification_As_Seen(BaseModel):
    noti_id: str = Field(default=None, description='ID of notification/mark as read all if noti_id is None')

