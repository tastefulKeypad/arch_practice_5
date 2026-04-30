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
import schemas.user, schemas.token
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

passwordHash = PasswordHash.recommended()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/clientService", tags=["clientService"])

# ====================== Endpoints ======================
@router.post("/create_user", response_model=schemas.user.UserResponse)
def create_user(
    user: schemas.user.UserCreate,
    db: Session = Depends(appdb.GetDB)
):
    """
    Create a new user and add him to database
    """
    dbUser = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if dbUser:
        RaiseExceptionUserRegistered()

    # Hash password and store user credentials to db
    newUser = models.User(**user.model_dump())
    newUser.password = passwordHash.hash(newUser.password)
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser

@router.get("/get_all_users", response_model=List[schemas.user.UserResponse])
def get_users(
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Get list of all registered users 

    Must be admin to use this endpoint
    """
    if not tokenUser.isAdmin:
        RaiseExceptionAdmin()
    return db.query(models.User).all()



@router.get("/get_user_by_email", response_model=schemas.user.UserResponse)
def get_user_by_email(
    email: str,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Get user with given email (login)

    Must be admin to use this endpoint
    """
    if not tokenUser.isAdmin:
        RaiseExceptionAdmin()

    dbUser = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not dbUser:
        RaiseExceptionNoUser()
    return dbUser

@router.get("/get_user_by_name_and_surname", response_model=List[schemas.user.UserResponse])
def get_user_by_name_and_surname(
    name: str,
    surName: str,
    tokenUser: Annotated[models.User, Depends(GetTokenUser)],
    db: Session = Depends(appdb.GetDB)
):
    """
    Get all users with given name and surname

    Must be admin to use this endpoint
    """
    if not tokenUser.isAdmin:
        RaiseExceptionAdmin()

    dbUser = db.query(models.User).filter(
        (models.User.name == name) &
        (models.User.surName == surName)
    ).all()

    if not dbUser:
        RaiseExceptionNoUser()
    return dbUser
