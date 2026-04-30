from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
import yaml
import time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports from local files
import db
import schemas
import endpoints
from db.database import Base, engine, SessionLocal
import db.database as appdb
import db.models as models
from endpoints.authService import router as authService
from endpoints.rentService import router as rentService
from endpoints.clientService import router as clientService
from endpoints.autoParkService import router as autoParkService

# ==================== Init FastAPI app ====================
# Create database tables if they dont exist yet
Base.metadata.create_all(bind=engine)

security = HTTPBasic()
app = FastAPI()
app.include_router(authService)
app.include_router(rentService)
app.include_router(clientService)
app.include_router(autoParkService)

# Dump documentation into yaml format
if __name__ == "__main__":
    with open("openapi.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(app.openapi(), f, sort_keys=False, allow_unicode=True)


################# Endpoints #################
@app.get("/")
def read_root():
    return {"message": "Public endpoint"}

@app.post("/populate_db")
def populate_db(
    db: Session = Depends(appdb.GetDB)
):
    """
    Populates db with admin, users and cars for debug 

    To authorize as admin:

    email: admin@example.com
    
    pass:  admin

    To authorize as normal user:

    email: user1@example.com 

    pass:  user

    """
    passwordHash = PasswordHash.recommended()
    userCount = db.query(models.User).count()
    if userCount != 0:
        return {"message": "Database must be empty in order to populate it! Try to delete 'app.db' and try again"}

    users = [
        models.User(
            email="admin@example.com",
            name="Admin",
            surName="Adminovich",
            password=passwordHash.hash("admin"),
            isAdmin=True
        ),
        models.User(
            email="user1@example.com",
            name="Pyotr",
            surName="Novikov",
            password=passwordHash.hash("user"),
            isAdmin=False
        ),
        models.User(
            email="user2@example.com",
            name="Sergei",
            surName="Novikov",
            password=passwordHash.hash("user"),
            isAdmin=False
        ),
        models.User(
            email="user3@example.com",
            name="Andrey",
            surName="Kolmogorov",
            password=passwordHash.hash("user"),
            isAdmin=False
        )
    ]
    cars = [
        models.Car(
            carClass=1,
            price=600,
            capacity=4,
            name="Maybach"
        ),
        models.Car(
            carClass=2,
            price=300,
            capacity=2,
            name="Porsche"
        ),
        models.Car(
            carClass=3,
            price=200,
            capacity=4,
            name="Lexus"
        ),
        models.Car(
            carClass=4,
            price=100,
            capacity=4,
            name="Ford"
        ),
        models.Car(
            carClass=5,
            price=50,
            capacity=4,
            name="Skoda"
        )
    ]
    db.add_all(users)
    db.add_all(cars)
    db.commit()
    return {"message": "Successfully populated db with basic objects"}
    
