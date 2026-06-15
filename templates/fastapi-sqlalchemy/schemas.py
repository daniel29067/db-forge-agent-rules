from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Base configuration for Pydantic models to interact with SQLAlchemy
class BaseConfigModel(BaseModel):
    class Config:
        from_attributes = True


# Standard model containing shared audit attributes for responses
class AuditResponse(BaseConfigModel):
    created_at: datetime
    updated_at: datetime
    is_active: bool


# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Captured on input only

class UserResponse(UserBase, AuditResponse):
    id: int


# --- Tag Schemas ---
class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase, AuditResponse):
    id: int


# --- PostTag Junction Schema ---
# Standard DTO representing the explicit associative entity
class PostTagResponse(BaseConfigModel):
    tag_id: int
    tag: TagResponse


# --- Post Schemas ---
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str

class PostCreate(PostBase):
    tag_ids: List[int] = []  # Pass tag list explicitly on creation

class PostResponse(PostBase, AuditResponse):
    id: int
    author_id: int
    post_tags: List[PostTagResponse] = []
