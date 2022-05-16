from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


#==================================================================
#=========================CREATE_GROUP=============================
#==================================================================
class GroupAddress(BaseModel):
    group_commune: str = Field(default=None, description='xã/phường')
    group_district: str = Field(default=None, description='quận/huyện')
    group_city: str = Field(default=None, description='tỉnh/thành phố')

class DATA_Create_Group(BaseModel):
    # user_id: str = Field(..., description='ID of user')
    group_name: str = Field(..., description='name of group')
    # group_label: str = Field(..., description='label of group')
    group_description: Optional[str] = Field(default=None, description='description of group')
    # group_address: Optional[GroupAddress] = Field(default=None, description='group address')
    group_type: str = Field(default='public', enum=['public', 'private'])
    group_avatar: HttpUrl = Field(..., description='avatar of group')
    group_cover_image: HttpUrl = Field(default=None, description='cover image of group')
    
#==================================================================
#==========================GROUP_LABEL=============================
#==================================================================
class DATA_Group_Label(BaseModel):
    name: str = Field(..., description='name of label')
    sales: str = Field(..., description='doanh số')
    num_person: str = Field(..., description='số người')
    num_place: str = Field(..., description='số điểm bán')
    local: str = Field(..., description='địa bàn')
    knowledge: str = Field(..., description='kiến thức')
    time: str = Field(..., description='thời gian')
    income: str = Field(..., description='thu nhập')
    next_label: str = Field(default=None, description='danh hiệu tiếp theo')

#==================================================================
#=========================UPDATE_GROUP=============================
#==================================================================
class DATA_Update_Group(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # owner_id: str = Field(..., description='ID of owner')
    group_name: Optional[str] = Field(default=None, description='name of group')
    group_description: Optional[str] = Field(default=None, description='description of group')
    # group_address: Optional[GroupAddress] = Field(default=None, description='group address')
    group_type: Optional[str] = Field(default='public', enum=['public', 'private'])
    # group_label: Optional[str] = Field(default=None, description='label of group')
    # group_avatar: Optional[str] = Field(..., description='avatar of group')
    # group_cover_image: Optional[str] = Field(default=None, description='cover image of group')

class DATA_Update_Group_Chat(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # owner_id: str = Field(..., description='ID of owner')
    group_chat_id: str = Field(..., description='ID of group_chat')

class DATA_Update_Group_image(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # owner_id: str = Field(..., description='ID of owner')
    image_type: str = Field(..., description='avatar/cover')
    image_url: str = Field(..., description='image url')

#==================================================================
#=========================INVITE_MEMBERS===========================
#==================================================================
class DATA_Invite_Members(BaseModel):
    # user_id: str = Field(..., description='ID of owner')
    list_user_ids: List[str] = Field(default=[], description='list user_id will be invite to join in group')

#==================================================================
#======================ACCEPT_INVITATION===========================
#==================================================================
class DATA_Accept_invitation(BaseModel):
    invitation_id: str = Field(..., description='ID of invitation')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#======================REJECT_INVITATION===========================
#==================================================================
class DATA_Reject_invitation(BaseModel):
    invitation_id: str = Field(..., description='ID of invitation')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#======================CANCEL_INVITATION===========================
#==================================================================
class DATA_Cancel_invitation(BaseModel):
    invitation_id: str = Field(..., description='ID of invitation')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#===================SEND_REQUEST_JOIN_GROUP========================
#==================================================================
class DATA_Join_Request(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#==================ACCEPT_REQUEST_JOIN_GROUP=======================
#==================================================================
class DATA_Accept_Join_Request(BaseModel):
    request_id: str = Field(..., description='ID of group')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#==================REJECT_REQUEST_JOIN_GROUP=======================
#==================================================================
class DATA_Reject_Join_Request(BaseModel):
    request_id: str = Field(..., description='ID of group')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#==================CANCEL_REQUEST_JOIN_GROUP=======================
#==================================================================
class DATA_Cancel_Join_Request(BaseModel):
    request_id: str = Field(..., description='ID of group')
    # user_id: str = Field(..., description='ID of user')

#==================================================================
#===================REMOVE_GROUP_MEMBERS===========================
#==================================================================
class DATA_Remove_Members(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # owner_id: str = Field(..., description='ID of owner')
    list_user_ids: List[str] = Field(default=[], description='list user_id will be remove out of group')

#==================================================================
#===========================DELETE_GROUP===========================
#==================================================================
class DATA_Delete_Group(BaseModel):
    group_id: str = Field(..., description='ID of group')
    # owner_id: str = Field(..., description='ID of owner')

#==================================================================
#====================LIST_ALL_GROUP_CREATED========================
#==================================================================
class DATA_Group_created(BaseModel):
    page: int = Field(..., description='page number')

#==================================================================
#====================LIST_ALL_GROUP_BY_ADMIN=======================
#==================================================================
class DATA_Group_By_Admin(BaseModel):
    page: int = Field(default=1, description='page number')
    limit: int = Field(default=10, description='limit of num result')
    search: Optional[str] = Field(default=None, description='text search')
    group_label: str = Field(default=None, description='filter by group label')
    group_status: str = Field(default=None, description='filter by group status')
    group_type: str = Field(default=None, description='filter by group type')
    group_address: GroupAddress = Field(default=None, description='filter by group address')


class DATA_update_group_status(BaseModel):
    group_id: str = Field(..., description='group id')
    group_status: str = Field(..., description='enable/disable')