#  Copyright (c) 2021.
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field



#=========================================================================
#============================CREATE_GROUP=================================
#=========================================================================
class ImageInfo(BaseModel):
    secure_url: str
    public_id: str

class GroupInfo(BaseModel):
    _id: str
    owner_id: str
    group_name: str
    group_description: str
    group_type: str
    group_avatar: ImageInfo
    group_cover_image: ImageInfo
    time_created: str
    time_updated: str

class CreateGroupResponse200(BaseModel):
    status: str
    data: GroupInfo

class CreateGroupResponse400(BaseModel):
    status: str

#=========================================================================
#============================UPDATE_GROUP=================================
#=========================================================================
class UpdateGroupResponse200(BaseModel):
    status: str

class UpdateGroupResponse400(BaseModel):
    status: str

class UpdateGroupResponse403(BaseModel):
    status: str

class UpdateGroupResponse404(BaseModel):
    status: str

#=========================================================================
#========================ADD_USERS_TO_GROUP===============================
#=========================================================================
class AddUserResponse200(BaseModel):
    status: str
    list_ids: List[str]

class AddUserResponse403(BaseModel):
    status: str

class AddUserResponse404(BaseModel):
    status: str

#=========================================================================
#========================REMOVE_GROUP_MEMBERS=============================
#=========================================================================
class RemoveMemberResponse200(BaseModel):
    status: str

class RemoveMemberResponse403(BaseModel):
    status: str

class RemoveMemberResponse404(BaseModel):
    status: str

#=========================================================================
#=============================DELETE_GROUP================================
#=========================================================================
class DeleteGroupResponse200(BaseModel):
    status: str

class DeleteGroupResponse403(BaseModel):
    status: str

class DeleteGroupResponse404(BaseModel):
    status: str

#=========================================================================
#============================GET_GROUP_INFO===============================
#=========================================================================
class GroupInfoResponse200(BaseModel):
    status: str
    data: GroupInfo

class GroupInfoResponse400(BaseModel):
    status: str

class GroupInfoResponse404(BaseModel):
    status: str

#=========================================================================
#=========================LIST_ALL_GROUP_JOINED===========================
#=========================================================================
class AllGroupResponse200(BaseModel):
    status: str
    data: List[GroupInfo]

class AllGroupResponse400(BaseModel):
    status: str

#=========================================================================
#=============================ACCEPT_INVITATION===========================
#=========================================================================
class InvitationInfo(BaseModel):
    _id: str
    group_id: str
    user_id: str
    datetime_created: float

class AcceptInvitationResponse200(BaseModel):
    status: str
    data: InvitationInfo

class AcceptInvitationResponse404(BaseModel):
    status: str

#=========================================================================
#========================SEND_REQUEST_JOIN_GROUP==========================
#=========================================================================
class RequestJoinGroupResponse200(BaseModel):
    status: str
    request_id: str

class RequestJoinGroupResponse404(BaseModel):
    status: str


