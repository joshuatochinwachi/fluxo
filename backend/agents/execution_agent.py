from core.config import get_redis_connector
from core.pubsub.channel_manager import ChannelNames
import json
import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class execution_agent:
    def __init__(self):
        self.redis_db = get_redis_connector()
        
        # ADD YOUR LOGIC - DEX data
        self.dex_liquidity = {
            "merchant_moe": {"tvl": 50000000, "avg_slippage": 0.3, "gas": 0.50},
            "fusionx": {"tvl": 35000000, "avg_slippage": 0.4, "gas": 0.45},
            "agni_finance": {"tvl": 20000000, "avg_slippage": 0.6, "gas": 0.55}
        }
    
    # KEEP FREEMAN'S PUB/SUB STRUCTURE
    async def Receive_execution_data(self):
        await self.redis_db.connect()
        pubsub = self.redis_db.redis.pubsub()
        await pubsub.subscribe(ChannelNames.EXECUTION.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received execution data: {data}")
            
            # ===== ADD YOUR LOGIC HERE =====
            try:
                execution_data = json.loads(data) if isinstance(data, str) else data
                
                # YOUR EXECUTION PREVIEW LOGIC
                preview = await self.generate_preview(execution_data)
                
                # Publish results
                await self.redis_db.redis.publish(
                    'execution_complete_channel',
                    json.dumps(preview)
                )
                logger.info(f"✅ Execution preview: {preview['recommended_dex']}")
            except Exception as e:
                logger.error(f"❌ Execution failed: {str(e)}")
    
    # ADD YOUR PREVIEW METHOD
    async def generate_preview(self, execution_data: dict) -> dict:
        """Your execution preview logic"""
        amount_usd = execution_data.get("amount_usd", 0)
        
        # Select best DEX
        if amount_usd > 50000:
            dex = "merchant_moe"
        elif amount_usd > 10000:
            dex = "fusionx"
        else:
            dex = "merchant_moe"
        
        dex_data = self.dex_liquidity[dex]
        
        return {
            "recommended_dex": dex,
            "estimated_slippage": dex_data["avg_slippage"],
            "gas_cost_usd": dex_data["gas"],
            "liquidity_depth": "good",
            "timestamp": datetime.now(UTC).isoformat()
        }
