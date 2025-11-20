"""Application configuration helpers.

This module centralizes simple config values and environment-backed
settings. Keep secrets and credentials out of source control — set them
via environment variables or a secrets manager and reference them here.

Examples of URL formats for Celery broker/result-backend are below.

Redis broker/result backend:
	redis://[:password]@hostname:port/db
	e.g. redis://:s3cr3t@redis.example.com:6379/0


"""

import os
import logging
from pathlib import Path
from typing import Final
from pydantic_settings import BaseSettings, SettingsConfigDict

import motor.motor_asyncio
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s : %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

class Settings(BaseSettings):
    celery_broker_url: str 
    dune_api_key: str 
    database_url: str
    admin_email: str 
    redis_host:str
    redis_port:int
    redis_password:str
    twitter_bearer_token:str
    reddit_client_id:str
    reddit_client_secret:str
    anthropic_api_key:str
    gemini_api_key:str
    mongo_url:str


    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        case_sensitive=False
    )

# Redis database client
class Redisconnect:
   from models.redis_connect import db_connector
   

   redis_connector = db_connector(max_connections=5)
   redis_db = redis_connector.get_connection()

# Mongo Db database client
class MongodbConnect:
    
    
    def __init__(self):
        settings = Settings()
        self.mongo_url = settings.mongo_url
        # self.database_client = motor.motor_asyncio.AsyncIOMotorClient(
        #             self.mongo_url
        #         )
        self.database_client = MongoClient(self.mongo_url)
        self.database = self.database_client['FluxoBuild']

    def Mongo_Database(self):
        while True:
            try:
                self.database.command('ping')
                logging.info("✅ MongoDB connection established successfully.")
                return self.database
            except Exception as e:
                logging.error(f"❌ MongoDB connection failed!! Retrying...:")
                continue




REDIS_CONNECT = Redisconnect().redis_db
MONGO_CONNECT = MongodbConnect().Mongo_Database()

DEFILLAMA_URL_ENDPOINTS: Final[dict[str, str]] = {
    'protocols': 'https://api.llama.fi/protocols',
    'chains': 'https://api.llama.fi/chains',
    'defi': 'https://api.llama.fi/defi',
    'protocol': 'https://api.llama.fi/protocol/{protocol_slug}',
    'pools':'https://yields.llama.fi/pools'
}

DUNE_SERVICE_ENDPOINTS : Final[dict[str, str]] = {
    'balances':'https://api.sim.dune.com/v1/evm/balances',
    'token_info':'https://api.sim.dune.com/v1/evm/token-info'
}

MANTLE_RPC_URL = 'https://mantle.drpc.org'  # This is a public RPC endpoint for Mantle
MANTLE_WSS_URL = 'wss://mantle.drpc.org'  # WebSocket endpoint for Mantle



# Lazy loading function to avoid circular imports
def get_redis_connector():
    """Get Redis connector instance (lazy import to avoid circular dependency)"""
    from models.redis_connect import db_connector
    return db_connector
