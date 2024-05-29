from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email:EmailStr
    password:str

class UserOut(BaseModel):
    id:int
    email:EmailStr

    class Config:
        orm_mode:True


class UserLogin(BaseModel):
    email:EmailStr
    password:str


class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[int] = None


class RepoOperationSchema(BaseModel):
    repo_url: str


class FunctionBase(BaseModel):
    file_name: str
    function_name: str
    class_name: str = None
    code: str

class FunctionCreate(FunctionBase):
    pass

class FunctionRead(FunctionBase):
    id: int

    class Config:
        orm_mode = True