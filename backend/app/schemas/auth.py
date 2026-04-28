from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            email=obj.email,
            full_name=obj.full_name,
            role=obj.role
        )

    class Config:
        from_attributes = True