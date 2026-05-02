from datetime import datetime
import json
from db.database import redisClient
import schemas.car

def RedisCacheCars(
    dbCar: list,
    dateStart: datetime, 
    dateEnd: datetime
):
    cacheKey = f"available_cars:{dateStart.isoformat()}_{dateEnd.isoformat()}"
    dbCarData = json.dumps(
        [schemas.car.CarResponse.model_validate(car).model_dump() for car in dbCar])
    redisClient.setex(cacheKey, 60, dbCarData)

def RedisGetCachedCars(
    dateStart: datetime, 
    dateEnd: datetime
):
    cacheKey = f"available_cars:{dateStart.isoformat()}_{dateEnd.isoformat()}"
    cacheData = redisClient.get(cacheKey)
    if cacheData:
        return json.loads(cacheData)
    return None
