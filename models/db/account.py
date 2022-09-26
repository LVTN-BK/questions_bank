from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    name: str = Field(...)
    # token: Token = Field(...)
    # secret_key: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    # encrypt_password: str = Field(...)
    # encrypt_key: str = Field(...)
    key_verify: str = Field(...)
    is_verified: bool = Field(default=False)
    is_disable: bool = Field(default=False)
    datetime_created: datetime = Field(...)