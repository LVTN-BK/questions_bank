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
    username: str = Field(...)
    token: Token = Field(...)
    secret_key: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    encrypt_password: str = Field(...)
    encrypt_key: str = Field(...)
    datetime_created: datetime = Field(...)