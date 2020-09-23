import motor.motor_asyncio

from config import MONGO_HOST, MONGO_PORT, MONGO_DBNAME
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST, MONGO_PORT)
mongodb = client[MONGO_DBNAME]


async def get_groups():
    cursor = mongodb.groups.find()
    datas = []
    async for item in cursor:
        datas.append(item['name'])
    return datas
