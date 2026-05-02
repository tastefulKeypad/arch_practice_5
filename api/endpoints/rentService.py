from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
import db.database as appdb
import db.models as models
import schemas.car, schemas.rent, schemas.token
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

passwordHash = PasswordHash.recommended()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/rentService", tags=["rentService"])

# ====================== Endpoints ======================
@router.post("/add_rent", response_model=schemas.rent.RentResponse)
def add_rent(
    carId: int,
    dateStart: datetime,
    dateEnd: datetime,
    status: str,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Create a new rent and add it to database

    Must be normal user to use this endpoint
    """
    # Check that user is NOT admin, date is correct and car is available
    if tokenUser.isAdmin:
        RaiseExceptionUser()
    if (dateEnd < dateStart):
        RaiseExceptionInvalidDateInput()
    dbCar = db.query(models.Car).filter(
        models.Car.id == carId
    ).first()
    if not dbCar:
        RaiseExceptionNoCar()
    dbBadCar = db.query(models.Rent).filter(
        (dateStart < models.Rent.dateEnd) &
        (dateEnd   > models.Rent.dateStart) &
        (models.Rent.status == "Active") &
        (models.Rent.carId  == carId)
    ).first()
    if dbBadCar:
        RaiseExceptionCarIsReserved()
    newRent = models.Rent(
        carId = carId,
        userId = tokenUser.id,
        dateStart = dateStart,
        dateEnd = dateEnd,
        status = status
    )
    db.add(newRent)
    db.commit()
    db.refresh(newRent)
    return newRent

@router.get("/get_active_rent", response_model=List[schemas.rent.RentResponse])
def get_active_rent(
    userId: int,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Get a list of all active rents by given user id

    Normal users can only query for their own id

    Admins can query for any user id
    """
    # Check that user is NOT admin, date is correct and car is available
    if not tokenUser.isAdmin:
        if tokenUser.id != userId:
            RaiseExceptionAdmin()
        dbRents = db.query(models.Rent).filter(
            (models.Rent.userId == userId) &
            (models.Rent.status == "Active")
        ).all()
        return dbRents

    dbUser = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not dbUser:
        RaiseExceptionNoUser()
    dbRents = db.query(models.Rent).filter(
        (models.Rent.userId == userId) &
        (models.Rent.status == "Active")
    ).all()
    return dbRents

@router.get("/get_rent_history", response_model=List[schemas.rent.RentResponse])
def get_rent_history(
    userId: int,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Get history of rents by given user id

    Normal users can only query for their own id

    Admins can query for any user id
    """
    if not tokenUser.isAdmin:
        if tokenUser.id != userId:
            RaiseExceptionAdmin()
        dbRents = db.query(models.Rent).filter(
            models.Rent.userId == userId
        ).all()
        return dbRents

    dbUser = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not dbUser:
        RaiseExceptionNoUser()
    dbRents = db.query(models.Rent).filter(
        models.Rent.userId == userId
    ).all()
    return dbRents

@router.patch("/finish_rent", response_model=schemas.rent.RentResponse)
def finish_rent(
    id: int,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Finalize rent and change it's state from 'Active' to 'Inactive'

    Must be admin to use this endpoint
    """
    if not tokenUser.isAdmin:
        RaiseExceptionAdmin()

    dbRent = db.query(models.Rent).filter(
        (models.Rent.id == id) &
        (models.Rent.status == "Active")
    ).first()
    if not dbRent:
        RaiseExceptionValidRentNotFound()

    dbRent.status = "Inactive"
    db.add(dbRent)
    db.commit()
    db.refresh(dbRent)
    return dbRent
