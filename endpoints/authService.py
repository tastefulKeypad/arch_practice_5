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
router = APIRouter()

# ====================== Endpoints ======================
@router.post("/token")
def login_for_token(
    formData: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(appdb.GetDB)
) -> schemas.token.Token:
    user = AuthenticateUser(formData.username, formData.password, db)
    if not user:
        RaiseExceptionBadCredentials()
    accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    accessToken = CreateAccessToken(
        data={"sub": user.email},
        expiresDelta=accessTokenExpires
    )
    return schemas.token.Token(access_token=accessToken, token_type="bearer")
