from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    email    = Column(String,  nullable=False)
    name     = Column(String,  nullable=False)
    surName  = Column(String,  nullable=False)
    password = Column(String,  nullable=False)
    isAdmin  = Column(Boolean, nullable=False)

class Car(Base):
    __tablename__ = "cars"
    id       = Column(Integer, primary_key=True, index=True)
    carClass = Column(Integer, nullable=False)
    price    = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    name     = Column(String,  nullable=False)

class Rent(Base):
    __tablename__ = "rents"
    id        = Column(Integer,  primary_key=True, index=True)
    carId     = Column(Integer,  nullable=False)
    userId    = Column(Integer,  nullable=False)
    dateStart = Column(DateTime, nullable=False)
    dateEnd   = Column(DateTime, nullable=False)
    status    = Column(String,   nullable=False)
