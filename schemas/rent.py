from pydantic import BaseModel
from datetime import datetime

class RentBase(BaseModel):
    """Base schema with common rent fields"""
    carId: int
    userId: int
    dateStart: datetime
    dateEnd: datetime
    status: str

class RentCreate(RentBase):
    """Schema for creating a new rent"""
    pass

class RentResponse(RentBase):
    """Schema with rent response"""
    id: int
    class Config:
        from_attributes = True
