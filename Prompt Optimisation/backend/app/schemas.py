from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PromptVersionResponse(BaseModel):
    id: int
    prompt_id: int
    version_number: int
    content: str
    model: str
    change_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PromptMetadataResponse(BaseModel):
    id: int
    prompt_id: int
    performance_score: int
    token_count: int
    usage_count: int
    last_used: Optional[datetime]
    custom_data: dict

    class Config:
        from_attributes = True


class PromptBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    model: str = "gpt-3.5-turbo"
    tags: Optional[List[str]] = []


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    model: Optional[str] = None
    tags: Optional[List[str]] = None


class PromptResponse(PromptBase):
    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    versions: List[PromptVersionResponse] = []
    metadata: Optional[PromptMetadataResponse] = None

    class Config:
        from_attributes = True


class VersionCreateRequest(BaseModel):
    content: str
    model: str = "gpt-3.5-turbo"
    change_description: Optional[str] = None


class VersionComparisonResponse(BaseModel):
    version_1_id: int
    version_2_id: int
    version_1_content: str
    version_2_content: str
    differences: List[str]


class TokenRequest(BaseModel):
    access_token: str
    token_type: str


class PromptListResponse(BaseModel):
    total: int
    prompts: List[PromptResponse]
