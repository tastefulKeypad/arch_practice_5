from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
import db.database as appdb
import db.models as models
import schemas.user, schemas.token
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

passwordHash = PasswordHash.recommended()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ================ Common HTTPExceptions ================
def RaiseExceptionAdmin():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be admin to use this endpoint",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionUser():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be a normal user to use this endpoint",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionUserRegistered():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionInvalidDateInput():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Date input is invalid",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionCarIsReserved():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Car is already reserved for this date window",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionValidRentNotFound():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not find active valid rent entry",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionNoUser():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find user",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionNoCar():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find car",
        headers={"WWW-Authenticate": "Bearer"}
    )

def RaiseExceptionBadCredentials():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# ================ Common functions ================
def VerifyPassword(plainPassword, hashedPassword):
    return passwordHash.verify(plainPassword, hashedPassword)

def AuthenticateUser(
    email: str,
    password: str,
    db: Session
):
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()
    if not user:
        return False
    if not VerifyPassword(password, user.password):
        return False
    return user

def CreateAccessToken(
    data: dict, 
    expiresDelta: timedelta | None = None
):
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJwt

def GetTokenUser(
    token: Annotated[str, Depends(oauth2Scheme)],
    db: Session = Depends(appdb.GetDB)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            RaiseExceptionBadCredentials()
        tokenData = schemas.token.TokenData(username=username)
    except InvalidTokenError:
        RaiseExceptionBadCredentials()
    user = db.query(models.User).filter(
        models.User.email == tokenData.username
    ).first()
    if user is None:
        RaiseExceptionBadCredentials()
    return user
