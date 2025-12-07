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
from redis.asyncio import Redis

import os
from dotenv import load_dotenv

load_dotenv()

# Social Media APIs
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")

# Validate critical keys
if not TWITTER_API_KEY:
    print("⚠  WARNING: TWITTER_API_KEY not set in .env")

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
    apitube_news:str
    coindesk_news:str
    etherscan:str
    twitter_api_key:str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        case_sensitive=False
    )

# Redis database client
# NOTE: avoid creating Redis connector at import time to prevent circular
# imports (models.redis_connect imports core.config.Settings). Use the
# `get_redis_connection` helper below which performs a lazy import and
# returns a Redis connection instance on demand.



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


class redisConnect:
    def __init__(self):
        settings = Settings()

        self.db_connect = Redis(
            host='localhost',
            port=6379,
            db=1
            # host=settings.redis_host,
            # port=settings.redis_port,
            # password=settings.redis_password,
            # max_connections=max_connections
        )
     
    def get_connection(self, db=None):
        redis_connect = self.db_connect
        return redis_connect


# Backwards-compatible placeholder. Call `get_redis_connection()` instead
# of relying on an import-time instance.
REDIS_CONNECT = None
MONGO_CONNECT = None

DEFILLAMA_URL_ENDPOINTS: Final[dict[str, str]] = {
    'protocols': 'https://api.llama.fi/protocols',
    'chains': 'https://api.llama.fi/chains',
    'defi': 'https://api.llama.fi/defi',
    'protocol': 'https://api.llama.fi/protocol/{protocol_slug}',
    'pools':'https://yields.llama.fi/pools'
}

DUNE_SERVICE_ENDPOINTS : Final[dict[str, str]] = {
    'balances':'https://api.sim.dune.com/v1/evm/balances',
    'token_info':'https://api.sim.dune.com/v1/evm/token-info',
    'transaction':'https://api.sim.dune.com/v1/evm/transactions'
}

MANTLE_RPC_URL = 'https://mantle.drpc.org'  # This is a public RPC endpoint for Mantle
MANTLE_WSS_URL = 'wss://mantle.drpc.org'  # WebSocket endpoint for Mantle



def get_redis_connection(max_connections: int = 5):
    connector = redisConnect()
    return connector.get_connection()

def get_mongo_connection():
    connector = MongodbConnect()
    return connector.Mongo_Database()
