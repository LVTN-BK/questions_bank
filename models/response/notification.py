#  Copyright (c) 2021.
from datetime import datetime
from tokenize import Double
from typing import List, Optional
from pydantic import BaseModel



#=========================================================================
#=========================GET_ALL_NOTIFICATION============================
#=========================================================================
class TargetInfo(BaseModel):
    target_id: str
    target_type: str

class AllNotidicationInfo(BaseModel):
    noti_id: str
    sender_id: str
    noti_type: str
    content: str
    target: TargetInfo
    is_read: bool
    datetime_created: float

class AllNotificationResponse200(BaseModel):
    status: str
    data: List[AllNotidicationInfo]

class AllNotificationResponse404(BaseModel):
    status: str

#=========================================================================
#====================CREATE_NOTIFICATION_TO_GROUP_MEMBERS=================
#=========================================================================
class NotificationInfomation(BaseModel):
    noti_id: str
    sender_id: str
    noti_type: str
    content: str
    target: TargetInfo
    datetime_created: float

class CreateNotificationGroupResponse200(BaseModel):
    status: str
    data: NotificationInfomation

#=========================================================================
#===================CREATE_NOTIFICATION_TO_ALL_SYSTEM_USER================
#=========================================================================
class CreateNotificationSystemResponse200(BaseModel):
    status: str
    data: NotificationInfomation

#=========================================================================
#======================CREATE_NOTIFICATION_TO_LIST_USER===================
#=========================================================================



class CreateNotificationListUserResponse200(BaseModel):
    status: str
    data: NotificationInfomation

#=========================================================================
#=========================DELETE_NOTIFICATION=============================
#=========================================================================
class DeleteNotificationResponse200(BaseModel):
    status: str

class DeleteNotificationResponse400(BaseModel):
    status: str

#=========================================================================
#====================MARK_NOTIFICATION_AS_SEEN(READ)======================
#=========================================================================
class MarkNotificationAsSeenResponse200(BaseModel):
    status: str

class MarkNotificationAsSeenResponse400(BaseModel):
    status: str

#=========================================================================
#=========================ALL_UNREAD_NOTIFICATION=========================
#=========================================================================
class UnreadNotificationResponse200(BaseModel):
    status: str
    data: List[NotificationInfomation]

class UnreadNotificationResponse404(BaseModel):
    status: str

#=================================================================
#======================INITIAL_NOTIFICATION_SETTING===============
#=================================================================
class InitNotificationSetting200(BaseModel):
    status: str

#=================================================================
#======================UPDATE_NOTIFICATION_SETTING================
#=================================================================
class UpdateNotificationSetting200(BaseModel):
    status: str




