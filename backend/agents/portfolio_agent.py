import asyncio
import json
from typing import List

from datetime import datetime,timezone
from dataclasses import asdict, is_dataclass
from core.config import REDIS_CONNECT, get_mongo_connection, get_redis_connection
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.pipeline import Pipeline

class portfolio_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.mongo = get_mongo_connection()
        try:
            self.redis_db = get_redis_connection()
        except Exception as e:
            print(f"Redis connection failed in portfolio_agent: {e}")
            self.redis_db = None

    # Receives processed market data from market_agent
    async def retrieve_portfolio_data(self,wallet_address:str):
        try:
            # cache_key = f"user_portfolio:{wallet_address}"
            # if cached_data := await self.redis_db.get(cache_key):
            #     print('Using Cached Portfolio Data')
            #     return json.loads(cached_data)

            store_id = 'Portfolios'
            portfolio_collection = self.mongo['User_Portfolios']
            users_portfolios_datas = portfolio_collection.find_one({"_id":store_id})

            user_portfolio = None
            if users_portfolios_datas:
                user_portfolio = users_portfolios_datas.get(wallet_address)

            if not user_portfolio:
                user_portfolio = await self.analyze_portfolio(wallet_address)
                
            if user_portfolio:
                # Convert to dicts for caching if they are dataclasses
                data_to_cache = [asdict(item) if is_dataclass(item) else item for item in user_portfolio]
                # await self.redis_db.setex(cache_key, 600, json.dumps(data_to_cache, default=str))

            return user_portfolio  
        except Exception as e:
            print(f'There is error in retrieving wallet {wallet_address} portfolio. isssue {e}')     
    
    async def analyze_portfolio(self,none_track_address:bool=False)->List:
        """
        Fetch the wallet porfolio
        Save to db if the wallet is been monitored

        Other component uses this Function: ie they call with address
        """
        pipeline = Pipeline()
        try:
            if not none_track_address:
                if self.redis_db:
                    tracked_wallet = await self.redis_db.smembers("tracked_wallets")
                else:
                    tracked_wallet = []
            else:
                tracked_wallet = [none_track_address]
            
            for wallet_address in tracked_wallet:
                
                wallet_portfolio = await pipeline.user_portfolio(wallet_address.decode() if not none_track_address else wallet_address)
                if not none_track_address:
                    asyncio.create_task(self._update_user_portfolio(wallet_address.decode(),wallet_portfolio))
                else:
                    return wallet_portfolio
        except Exception as e:
            print(f"There is an issue analyzing user portfolio. Issue {e}")
            
    async def _update_user_portfolio(self,wallet_address:str,wallet_portfolio:list)->None:
        print('Storing User Portfolio Data')
        try:
            store_id = 'Portfolios'
            portfolio_collection = self.mongo['User_Portfolios']
            portfolio_data = [asdict(data) for data in wallet_portfolio]
            portfolio_collection.update_one(
                {"_id":f"{store_id}"},
                {
                    "$set":{
                        wallet_address:portfolio_data,
                        'updated_at':datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f'There is an error updatiing User transaction. issue: {e}')
    