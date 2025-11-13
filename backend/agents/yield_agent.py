from typing import List
from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames
from services.data_pipeline import DataSource

class yield_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.source = DataSource()


    # Fetch yield protocol and yields
    async def yield_opportunity(self):
        yield_protocols = await self.source.fetch_mantle_yield_protocols()

        return yield_protocols
        
