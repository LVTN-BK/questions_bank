from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse200(BaseModel):
    token: Token = Field(..., description='Access token')
    secret_key: str = Field(..., description='Secret key')


class LoginResponse403(BaseModel):
    status: str = Field(default="Failed")

class CreateAccountResponse200(BaseModel):
    status: str = "Created"
    access_token: str = Field(..., description='Access token for accessing others API')

class CreateAccountResponse403(BaseModel):
    status: str = "Failed"
    msg: str = "Email, Phone or UID is existing for another account"

class GetAccount200(BaseModel):
    email: str = Field(..., description='email')
    password: str = Field(..., description='password')
    instance_url: str = Field(..., description='aws instance url')


class GetAccount403(BaseModel):
    status: str = Field(default="Failed")

class User(BaseModel):
    username: str
    token: Token
    secret_key: str
    email: EmailStr
    hashed_password: str
    encrypt_password: str
    encrypt_key: str
    datetime_created: datetime