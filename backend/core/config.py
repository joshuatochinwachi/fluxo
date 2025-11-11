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
from pathlib import Path
from typing import Final
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import redis

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
     

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        case_sensitive=False
    )


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
