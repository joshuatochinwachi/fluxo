import ast
import asyncio
from typing import List
from core.config import get_redis_connection
from core.pubsub.channel_manager import ChannelNames
import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class onchain_agent:
    def __init__(self):
        self.redis_db = get_redis_connection()
        
        # ADD YOUR LOGIC - Whale thresholds
        self.whale_thresholds = {
            "MNT": 1000000,
            "mETH": 500000,
            "USDC": 2000000,
            "default": 100000
        }
    
    async def Receive_onchain_transfer(self):
        """
        Recieves Larger token transfer Event From Onchain 
        Pass it to smart money process
        pass it to whale detection Process
        """
        
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.ONCHAIN.value)

        async for message in pubsub.listen():
            try:
                if message['type'] != 'message':
                    print('No Data for onchaiin')
                    continue
                data = message['data']
                print(f"Received onchain transfer data: {data}")
                # Process the onchain transfer data as needed

                whale_threshold = 100_000
                data = data.decode('utf-8')
                data = ast.literal_eval(data)
                if float(data['amount_usd']) > whale_threshold: # TODO change the equality
                    continue
            
                # Lazy Import (Avoid Circular Error)
                from agents.orchestrator import AlertOrchestrator

                # Push To Alert Porcessor 
                alert = AlertOrchestrator()
                asyncio.create_task(alert.process_event(data))
                
            except:
                pass

            # # pubslish the whale data to other agents listening.
            # await self.redis_db.publish(ChannelNames.WHALE_MOVEMENT, data)
            
            # # ===== ADD YOUR WHALE DETECTION LOGIC HERE =====
            # try:
            #     transfer_data = json.loads(data) if isinstance(data, str) else data
                
            #     # YOUR WHALE DETECTION
            #     whale_analysis = await self.detect_whale(transfer_data)
                
            #     # Only publish if whale detected
            #     if whale_analysis["is_whale"]:
            #         await self.redis_db.redis.publish(
            #             'whale_watch_channel',
            #             json.dumps(whale_analysis)
            #         )
            # #         logger.info(f"🐋 Whale detected: {whale_analysis['summary']}")
            # except Exception as e:
            #     logger.error(f"❌ Whale detection failed: {str(e)}")
    
    # ADD YOUR WHALE DETECTION METHOD
    async def detect_whale(self, transfer_data: dict) -> dict:
        """Your whale detection logic"""
        token = transfer_data.get("token", "")
        amount_usd = float(transfer_data.get("amount_usd", 0))
        
        threshold = self.whale_thresholds.get(token, self.whale_thresholds["default"])
        is_whale = amount_usd >= threshold
        
        return {
            "is_whale": is_whale,
            "amount_usd": amount_usd,
            "threshold": threshold,
            "token": token,
            "summary": f"{'🐋 WHALE' if is_whale else '🐟 Regular'}: ${amount_usd:,.0f} {token}",
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    
            
