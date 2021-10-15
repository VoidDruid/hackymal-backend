import motor.motor_asyncio

from settings import mongo_settings


mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_settings.uri)

mongo = mongo_client[mongo_settings.db]
