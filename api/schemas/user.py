from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base schema with common user fields"""
    email: EmailStr
    name: str
    surName: str
    isAdmin: bool

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str

class UserResponse(UserBase):
    """Schema with user response"""
    id: int
    class Config:
        from_attributes = True
