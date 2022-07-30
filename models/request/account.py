from pydantic import BaseModel, EmailStr, Field



class DATA_Update_Account(BaseModel):
    name: str = Field(default=None, description='name of user')
    phone: str = Field(default=None, description='phone number')
    address: str = Field(default=None, description='address of user')
    gender: str = Field(default=None, description='gender of user')
    birthday: str = Field(default=None, description='birthday of user')

class DATA_Update_Email(BaseModel):
    email: EmailStr = Field(..., description='new email address')
    password: str = Field(..., description='user password')

class DATA_Update_Password(BaseModel):
    old_password: str = Field(..., description='old password')
    new_password: str = Field(..., description='new password')

class DATA_Reset_Password(BaseModel):
    email: EmailStr = Field(..., description='Email khôi phục mật khẩu')

class DATA_Apply_Reset_Password(BaseModel):
    keyonce: str = Field(..., description='Mã một lần để khôi phục mật khẩu'),
    password: str = Field(..., description='Mật khẩu lần một'),
    re_password: str = Field(..., description='Mật khẩu lần hai'),


