import asyncio
import json
import logging
import re
from typing import AsyncIterator

from .token_listener import TokenListener,TranferReponse
from services.dune_service import DuneService
from models.redis_connect import db_connector

logger = logging.getLogger(__name__)

class TokenWatcher:
    def __init__(self):
        self.token_listener = TokenListener()
        self.dune_service = DuneService()
        
        redis_connector = db_connector(max_connections=5)
        self.redis_db = redis_connector.get_connection()
        self.channel_name = "token_watch_channel"

    # Entry point to start watching transfers
    async def watch_transfers(self) -> AsyncIterator[dict]:
        while True:
            try:
                async for transfer_data in self.token_listener.tranfers_event():
                    # print(transfer_data)
                    asyncio.create_task(self.token_watch_updater(transfer_data))
            except Exception as e:
                logger.error(f"Error watching transfers: {e}")
                continue

    async def _fetch_token_data(self,token_address:str)-> dict:
        # This should only fetch token details users subscribed, to  avoid rate limit
        token_data = await self.dune_service.token_data(token_address)
        if not token_data:
            return None
        
        if "tokens" not in token_data:
            return None
        
        token_info = token_data['tokens'][0]
        return {
            'token':token_address,
            'price':token_info.get('price_usd',0),
            'symbol':token_info.get('symbol','Nan'),
            'decimal':token_info.get('decimals',18),
            'total_supply':token_info.get('total_supply',0)
        }
    
    async def token_watch_updater(self,transfer_data:TranferReponse)->None:
        if not transfer_data:
            return 
        
        token_address = transfer_data.token
        # Fetch Token Info 
        token_info = await self._fetch_token_data(token_address)
        if not token_info :
            return
        
        # Token infomation ------------------------------------
        token_price = float(token_info['price'])
        token_symbol = token_info['symbol']
        token_decimal = int(token_info['decimal'])
        token_supply = token_info['total_supply']

        # Transfer data info -------------------------------------
        amount_transfered = transfer_data.amount / 10**token_decimal
        amount_usd = amount_transfered * token_price
        from_address =  transfer_data.from_address
        to_address = transfer_data.to_address
        transaction_hash = transfer_data.transaction_hash
        block_number = transfer_data.block_number


        update_data = {
            'token':token_address,
            "amount_usd" : amount_usd,
            "from_address" :  from_address,
            "to_address" : to_address,
            "transaction_hash" :  transaction_hash,
            "symbol" : token_symbol,
            "block_number" :  block_number
        }

        # Publishing To Redis PubSub Channel
        update_data = json.dumps(update_data)
        await self.redis_db.publish(self.channel_name,update_data)
        print(f"📢 Published transfer event to channel {self.channel_name}: {update_data}")







