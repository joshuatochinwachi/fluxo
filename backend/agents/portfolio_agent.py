import asyncio
from typing import List

from datetime import datetime,timezone
from dataclasses import asdict
from core.config import REDIS_CONNECT, get_mongo_connection, get_redis_connection
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.pipeline import Pipeline

class portfolio_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.mongo = get_mongo_connection()
        self.redis_db = get_redis_connection()

    # Receives processed market data from market_agent
    async def retrieve_portfolio_data(self,wallet_address:str):
        store_id = 'Portfolios'
        try:
            portfolio_collection = self.mongo['User_Portfolios']
            if ( users_portfolios_datas := portfolio_collection.find_one({"_id":store_id})
                or {'null':'null'}
            ):
                user_portfolio = users_portfolios_datas.get(wallet_address)
                if not user_portfolio:
                    user_portfolio = await self.analyze_portfolio(wallet_address,True)

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
                tracked_wallet = await self.redis_db.smembers("tracked_wallets")
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
    