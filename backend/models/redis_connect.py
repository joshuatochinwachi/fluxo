from redis.asyncio import Redis
from core.config import Settings


settings = Settings()
class db_connector:
    def __init__(self,max_connections=3): 

        self.db_connect = Redis(
            host='localhost',
            port=6379,
            db=1
            # host=settings.redis_host,
            # port=settings.redis_port,
            # password=settings.redis_password,
            # max_connections=max_connections
            )
     
    def get_connection(self,db=None):
        redis_connect = self.db_connect
        return redis_connect