from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)

class LoginResponse200(BaseModel):
    token: Token = Field(..., description='Access token')
    secret_key: str = Field(..., description='Secret key')


class LoginResponse403(BaseModel):
    status: str = Field(default="Failed")

class CreateAccountResponse200(BaseModel):
    status: str = Field(default="Created")
    access_token: str = Field(..., description='Access token for accessing others API')

class CreateAccountResponse403(BaseModel):
    status: str = Field(default="Failed")
    msg: str = Field(default="Email, Phone or UID is existing for another account")

class GetAccount200(BaseModel):
    email: str = Field(..., description='email')
    password: str = Field(..., description='password')
    instance_url: str = Field(..., description='aws instance url')


class GetAccount403(BaseModel):
    status: str = Field(default="Failed")

class User(BaseModel):
    name: str = Field(...)
    # token: Token = Field(...)
    # secret_key: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    # encrypt_password: str = Field(...)
    # encrypt_key: str = Field(...)
    datetime_created: datetime = Field(...)

class PutResetPasswordResponse200(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Mật khẩu đã được thiết lập lại')

class PutResetPasswordResponse400(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Mã hết thời gian hoặc không tồn tại!')


class ResetPasswordResponse201(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Vui lòng kiểm tra email và nhập mã!')


class ResetPasswordResponse404(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Tài khoản không tồn tại!')