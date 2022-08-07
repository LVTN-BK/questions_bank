#  Copyright (c) 2021.
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Payload(BaseModel):
    id: str = Field(..., description='id of notification to use get detail notification')
    username: Optional[str] = Field(..., description='Username of the user who sent the notification')
    avatar: Optional[str] = Field(..., description='Avatar of user who sent the notification')
    content: Optional[str] = Field(..., description='Content of user who sent the notification')
    datetime_sent: Optional[str] = Field(..., description='Datetime when notification was sent')


class Notification(BaseModel):
    payload: Optional[Payload] = Field(..., description='Payload contain information for the notification')
    message: Optional[str] = Field(..., description='Message of the notification')
    type: Optional[str] = Field(..., description='Type of the notification')
    location: Optional[str] = Field(..., description='Where is the notification should be in?')
    user_id: int = Field(..., description='Id of user who will receive notification')


class NotificationTypeManage:
    COMMENT = 'Comment'
    GROUP_SHARE_QUESTION = 'group_share_question'
    COMMUNITY_SHARE_QUESTION = 'community_share_question'
    LOGGIN = 'Loggin'
    

class NotificationContentManage:
    COMMENT = 'đã bình luận vào đề thi của bạn'
    GROUP_SHARE_QUESTION = 'Bạn đã chia sẻ thành công một câu hỏi vào nhóm'
    COMMUNITY_SHARE_QUESTION = 'Bạn đã chia sẻ thành công một câu hỏi vào cộng đồng'
    LOGGIN = 'vừa đăng nhập thành công'