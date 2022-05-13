from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Group_DB(BaseModel):
    owner_id: str = Field(..., description='ID of owner of group')
    group_name: str = Field(..., description='name of group')
    group_description: str = Field(default=None, description='description of group')
    group_type: str = Field(default='public', enum=['public', 'private'])
    group_avatar: HttpUrl = Field(..., description='avatar of group')
    group_cover_image: HttpUrl = Field(default=None, description='cover image of group')
    datetime_created: float = Field(default=datetime.now().timestamp(), description='time create group')
    datetime_updated: float = Field(default=None, description='last time update group')
    group_status: str = Field(default='enable', description='status of group', enum=['enable', 'disable'])