from pydantic import BaseModel, Field

class CarBase(BaseModel):
    """Base schema with common car fields"""
    carClass: int
    price: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    name: str

class CarCreate(CarBase):
    """Schema for creating a new car"""
    pass

class CarResponse(CarBase):
    """Schema with car response"""
    id: int
    class Config:
        from_attributes = True
