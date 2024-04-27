from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    is_published: bool = True


class PostCreate(PostBase):
    pass


class PostCreate(PostBase):
    ...


class PostUpdate(PostBase):
    ...


class PostDelete(PostBase):
    ...


class PostInput(BaseModel):
    ...


class UserOutput(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOutput

    class Config:
        from_attributes = True


class PostOutput(BaseModel):
    Post: Post
    votes: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    direction: conint(ge=0, le=1)
