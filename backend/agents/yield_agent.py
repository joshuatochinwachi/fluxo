from typing import List,Dict, Any
from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames
from core.config import get_mongo_connection

class yield_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.mongo_db = get_mongo_connection()


    # Fetch yield protocol and yields
    async def yield_opportunity(self):

        try:
            yield_collection = self.mongo_db["Yield_Protocol"]
        except Exception:
            return {"opportunities": [], "summary": "mongo_unavailable"}

        store_id = "Mantle_yield_protocol"
        yield_protocol_data = yield_collection.find_one({"_id": store_id})

        if not yield_protocol_data:
            return {"opportunities": [], "summary": "no_pipeline_data"}

        protocols = (
            yield_protocol_data.get("protocol") or
            yield_protocol_data.get("yield_protocols") or
            []
        )

        def apy_of(p: Dict[str, Any]) -> float:
            try:
                return float(p.get("apy", 0) or p.get("estimated_apy", 0) or 0)
            except:
                return 0.0

        top_by_apy = sorted(protocols, key=apy_of, reverse=True)[:20]
        return top_by_apy
       
       
