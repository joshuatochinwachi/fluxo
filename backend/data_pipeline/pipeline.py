import asyncio
import json
import logging
from typing import AsyncIterator
from pydantic import BaseModel

from core.pubsub.channel_manager import ChannelNames
from models.redis_connect import db_connector

from .ingestion.defi_llama import Defillama
from .ingestion.dune_service import DuneService
from .ingestion.mantle_api import MantleAPI

from .transformation.transform_defillam_data import transform_protocol_data,transform_yield_protocol
from .transformation.transform_dune_data import transform_user_portfolio,transform_user_transaction_data
from .transformation.transform_mantleApi_data import transform_balance

from .load.store import StoreData

logger = logging.getLogger(__name__)

class TranferReponse(BaseModel):
    token: str
    from_address: str
    to_address: str
    amount: int
    transaction_hash: str
    block_number: int

class Pipeline:
    def __init__(self):
        self.defillama = Defillama()
        self.dune_service = DuneService()
        self.mantle_api = MantleAPI()
        
        self.storeData = StoreData()

        redis_connector = db_connector(max_connections=5)
        self.redis_db = redis_connector.get_connection()
       
    # For mantle protocols
    async def mantle_protocols(self):
        print('Started')
        protocol_data = await self.defillama.fetch_protocol_data()
        transformed_data =  transform_protocol_data(protocol_data)
        # print(transformed_data)
        if transformed_data:
            self.storeData.store_protocol_data(transformed_data,data_name="protocols")
            # Save to db
            pass
           
            
    
    # Yield in Mantle Ecosystem
    async def mantle_yield(self):
        yield_data = await self.defillama.fetch_mantle_yield_protocols()
        transformed_data = transform_yield_protocol(yield_data)
        if transformed_data: 
            self.storeData.store_protocol_data(transformed_data,data_name='yield_data')
            # save to db
           

    # User portfolio in Mantle
    async def user_portfolio(self,wallet_address:str):
        portfolio_data = await self.dune_service.user_portfolio_analysis(wallet_address)
        transformed_data = transform_user_portfolio(portfolio_data,wallet_address)
       
        if transformed_data:
            "Determine if to cache user portfolio "
            return transformed_data
    
    # Token Balance
    async def user_token_balance(self,token_address:str,wallet_address:str):
        balance_data = await self.mantle_api.get_token_balance(token_address,wallet_address)
        transformed_data = transform_balance(balance_data)
        return transformed_data
    
    # Mnt user balance
    async def user_mnt_balance(self,wallet_address:str):
        balance_data = await self.mantle_api.get_balance(wallet_address)
        transformed_data = transform_balance(balance_data)
        return transformed_data
    

    
    # Entry point to start watching transfers
    async def watch_transfers(self) -> AsyncIterator[dict]:
        while True:
            try:
                transfer_data = TranferReponse(
                    token='0x4515A45337F461A11Ff0FE8aBF3c606AE5dC00c9',
                    from_address='0xEd04925173FAD6A8e8939338ccF23244cae1fF12',
                    to_address='0xF354230053d4919A09508cdb3dff6a4E8e56643b',
                    amount=1000000000000,
                    transaction_hash='0xtest_hash',
                    block_number=123456
                )
                # async for transfer_data in self.mantle_api.tranfers_event():
                    # print(transfer_data)
                asyncio.create_task(self._token_watch_updater(transfer_data))
                await asyncio.sleep(20)
            except Exception as e:
                logger.error(f"Error watching transfers: {e}")
                continue

    
    async def _token_watch_updater(self,transfer_data:TranferReponse)->None:
        if not transfer_data:
            return 
        
        token_address = transfer_data.token
        # Fetch Token Info 
        token_info = await self.dune_service.token_data(token_address)
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
        await self.redis_db.publish(ChannelNames.ONCHAIN.value,update_data)
        print(f"📢 Published transfer event to channel {ChannelNames.ONCHAIN.value}: {update_data}")
   
    async def fetch_transactions(self,wallet_address:str):
        if not wallet_address.startswith('0x'):
            return {
                'transaction':False,
                'Error':'Invalid Address'
            }
        transaction_data = await self.mantle_api.user_transactions(wallet_address)
        # transformed_data = transform_user_transaction_data(transaction_data)
        return transaction_data

