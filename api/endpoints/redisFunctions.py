from datetime import datetime
import json
from db.database import redisClient
import db.models as models
import schemas.car

# ================ REDIS CACHE ================
def RedisCacheCars(
    dbCar: list,
    dateStart: datetime, 
    dateEnd: datetime
):
    """
    Cache given cars for given time period
    """
    cacheKey = f"available_cars:{dateStart.isoformat()}_{dateEnd.isoformat()}"
    dbCarData = json.dumps(
        [schemas.car.CarResponse.model_validate(car).model_dump() for car in dbCar])
    redisClient.setex(cacheKey, 60, dbCarData)

def RedisGetCachedCars(
    dateStart: datetime, 
    dateEnd: datetime
):
    """
    Get cached cars for given time period
    """
    cacheKey = f"available_cars:{dateStart.isoformat()}_{dateEnd.isoformat()}"
    cacheData = redisClient.get(cacheKey)
    if cacheData:
        return json.loads(cacheData)
    return None

# ================ CACHE INVALIDATION ================
def ParseKey(key: str):
    key = key.split(":", 1)[1]
    startStr, endStr = key.split("_")
    return datetime.fromisoformat(startStr), datetime.fromisoformat(endStr)

def RedisUpdateCacheAddCar(
    dbCar: models.Car,
    dateStart: datetime,
    dateEnd: datetime
):
    """
    Add cars to all overlapping date ranges
    """
    dbCarData = schemas.car.CarResponse.model_validate(dbCar).model_dump()
    for key in redisClient.scan_iter("available_cars:*"):
        cacheStartDate, cacheEndDate = ParseKey(key)
        if (dateEnd > cacheStartDate and dateStart < cacheEndDate):
            cachedCars = json.loads(redisClient.get(key))
            carExists = any(car.get('id') == dbCarData['id'] for car in cachedCars)
            if not carExists:
                cachedCars.append(dbCarData)
                newCacheValue = json.dumps(cachedCars)
                redisClient.setex(key, 60, newCacheValue)

def RedisUpdateCacheRemoveCar(
    dbCar: models.Car,
    dateStart: datetime,
    dateEnd: datetime
):
    """
    Remove cars from all overlapping date ranges
    """
    dbCarData = schemas.car.CarResponse.model_validate(dbCar).model_dump()
    for key in redisClient.scan_iter("available_cars:*"):
        cacheStartDate, cacheEndDate = ParseKey(key)
        if (dateEnd > cacheStartDate and dateStart < cacheEndDate):
            cachedCars = json.loads(redisClient.get(key))
            cachedCars = [car for car in cachedCars if car.get('id') != car_id]
            newCacheValue = json.dumps(cachedCars)
            redisClient.setex(key, 60, newCacheValue)

# ================ RATE LIMITING ================
def TokenBucketIsFull(userId: int):
    cacheKey = f"userid:{userId}"
    cacheValue = redisClient.get(cacheKey)
    if (cacheValue is None):
        return False
    return True if int(cacheValue) == 0 else False

def TokenBucketUpdate(userId: int):
    cacheKey = f"userid:{userId}"
    cacheValue = redisClient.get(cacheKey)
    if (cacheValue is None):
        cacheValue = 4;
        redisClient.setex(cacheKey, 60, cacheValue)
    elif (int(cacheValue) > 0):
        cacheTTL = redisClient.ttl(cacheKey)
        cacheValue = int(cacheValue)-1
        redisClient.setex(cacheKey, cacheTTL, cacheValue)
    return cacheValue
