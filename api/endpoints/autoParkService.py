from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
import db.database as appdb
import db.models as models
import schemas.car, schemas.token, schemas.rent
from endpoints.commonFunctions import *
from endpoints.redisFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

passwordHash = PasswordHash.recommended()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/autoParkService", tags=["autoParkService"])

# ====================== Endpoints ======================
@router.post("/add_car", response_model=schemas.car.CarResponse)
def add_car(
    car: schemas.car.CarCreate,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Create a new car and add it to database

    Must be admin to use this endpoint
    """
    if not tokenUser.isAdmin:
        RaiseExceptionAdmin()

    newCar = models.Car(**car.model_dump())

    db.add(newCar)
    db.commit()
    db.refresh(newCar)
    return newCar

@router.get("/get_all_cars", response_model=List[schemas.car.CarResponse])
def get_all_cars(
    db: Session = Depends(appdb.GetDB)
):
    """
    Get list of all cars
    """
    return db.query(models.Car).all()

@router.get("/get_car_by_class", response_model=List[schemas.car.CarResponse])
def get_car_by_class(
    carClass: int,
    db: Session = Depends(appdb.GetDB)
):
    """
    Get all cars with given class
    """
    dbCar = db.query(models.Car).filter(
        models.Car.carClass == carClass
    ).all()
    if not dbCar:
        RaiseExceptionNoCar()
    return dbCar

@router.get("/check_available_cars", response_model=List[schemas.car.CarResponse])
def check_available_cars(
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    dateStart: datetime,
    dateEnd:   datetime,
    db: Session = Depends(appdb.GetDB)
):
    """
    Get list of all available cars in given time frame

    Must be normal user or admin to use this endpoint

    Normal users are rate limited to 5 requests per minute
    """
    remainingTokens = "unlimited"
    if not tokenUser.isAdmin:
        if (TokenBucketIsFull(tokenUser.id)):
            RaiseExceptionRatelimitExceeded()
        remainingTokens = TokenBucketUpdate(tokenUser.id)

    redisCacheData = RedisGetCachedCars(dateStart, dateEnd)
    if redisCacheData is not None:
        if not redisCacheData:
            RaiseExceptionNoCar()
        return JSONResponse(content=redisCacheData,
                            headers={
                                "X-RateLimit-Limit": "5",
                                "X-RateLimit-Remaining": str(remainingTokens),
                                "X-RateLimit-Reset": "60",
                                }
                            )

    dbBadCars = db.query(models.Rent).filter(
        (dateStart < models.Rent.dateEnd) &
        (dateEnd   > models.Rent.dateStart) &
        (models.Rent.status == "Active") 
    ).all()
    dbBadIds = [badCar.carId for badCar in dbBadCars]
    dbCar = db.query(models.Car).filter(
        models.Car.id.notin_(dbBadIds)
    ).all()

    RedisCacheCars(dbCar, dateStart, dateEnd)
    if not dbCar:
        RaiseExceptionNoCar()
    dbCarData = [schemas.car.CarResponse.model_validate(car).model_dump() for car in dbCar]
    return JSONResponse(content=dbCarData,
                        headers={
                            "X-RateLimit-Limit": "5",
                            "X-RateLimit-Remaining": str(remainingTokens),
                            "X-RateLimit-Reset": "60",
                            }
                        )
