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
    COMMENT_QUESTION = 'comment_question'
    COMMENT_EXAM = 'comment_exam'
    REPLY_COMMENT = 'reply_comment'
    LIKE_QUESTION = 'like_question'
    LIKE_EXAM = 'like_exam'
    GROUP_SHARE_QUESTION = 'group_share_question'
    GROUP_SHARE_EXAM = 'group_share_exam'
    GROUP_INVITE_MEMBER = 'group_invite_member'
    GROUP_ACCEPT_REQUEST = 'group_accept_request'
    GROUP_REJECT_REQUEST = 'group_reject_request'
    USER_REQUEST_JOIN_GROUP = 'user_request_join_group'
    

class NotificationContentManage:
    COMMENT_QUESTION = 'đã bình luận vào câu hỏi của bạn'
    COMMENT_EXAM = 'đã bình luận vào đề thi của bạn'
    REPLY_COMMENT = 'đã trả lời bình luận của bạn'
    LIKE_QUESTION = 'đã thích câu hỏi của bạn'
    LIKE_EXAM = 'đã thích đề thi của bạn'
    GROUP_SHARE_QUESTION = 'đã chia sẻ một câu hỏi vào nhóm'
    GROUP_SHARE_EXAM = 'đã chia sẻ một đề thi vào nhóm'
    GROUP_INVITE_MEMBER = 'đã mời bạn vào nhóm'
    GROUP_ACCEPT_REQUEST = 'đã chấp nhận yêu cầu tham gia nhóm của bạn'
    GROUP_REJECT_REQUEST = 'đã từ chối yêu cầu tham gia nhóm của bạn'
    USER_REQUEST_JOIN_GROUP = 'đã gửi yêu cầu tham gia nhóm'