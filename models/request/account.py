from pydantic import BaseModel, Field



class DATA_Update_Account(BaseModel):
    name: str = Field(default=None, description='name of user')
    phone: str = Field(default=None, description='phone number')
    address: str = Field(default=None, description='address of user')
    gender: str = Field(default=None, description='gender of user')
    birthday: str = Field(default=None, description='birthday of user')