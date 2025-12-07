import ast
import asyncio
from typing import List
from core.config import get_mongo_connection, get_redis_connection
from core.pubsub.channel_manager import ChannelNames
import logging
from datetime import datetime, UTC,timezone

logger = logging.getLogger(__name__)


class onchain_agent:
    def __init__(self):
        self.redis_db = get_redis_connection()
        self.mongo = get_mongo_connection()
        
        # ADD YOUR LOGIC - Whale thresholds
        self.whale_thresholds = {
            "MNT": 1000000,
            "mETH": 500000,
            "USDC": 2000000,
            "default": 100000
        }
    async def retrieve_transcton_from_db(self,wallet_address:str,limit=None)->list:
        """
        Retrieve the transaction from the db
        Incase if the address is not among address monitored
        Fetch the address Transaction and not save 
        """
        try:
            store_id = "transactions"
            transaction_collection = self.mongo['User_Transaction']
            users_transactions_datas = transaction_collection.find_one({"_id":store_id})

            if not users_transactions_datas:
                return []
            
            user_transactions = users_transactions_datas.get(wallet_address)
            if not user_transactions:
                user_transactions = await self.fetch_transaction_and_update_db(wallet_address) 
                
            return user_transactions
        except Exception as e:
            print(f'There is an error Retrieving Wallet {wallet_address} transactions. Issue {e}')
        

    async def fetch_transaction_and_update_db(self,query_wallet_address:str=None)->None:
        """
            Fetch Users Transaction Data And update the db with the Newest data 
            query_wallet_addres denotes the address  searched from th frontend
            There is no need t store the transaction of a random address transaction searc in db
            We store only the transaction of the address we monitored for easier retrival
        """
        from data_pipeline.pipeline import Pipeline
        pipeline = Pipeline()

        try:
            if not query_wallet_address:
                tracked_wallet = await self.redis_db.smembers("tracked_wallets")
            else:
                tracked_wallet = [query_wallet_address]
            
            if not tracked_wallet:
                print('There is No Wallet To Fetch Transactions')
                return 
            
            for wallet_address in tracked_wallet:
                transaction_data = await pipeline.fetch_transactions(wallet_address.decode() if not query_wallet_address else wallet_address )
                if not query_wallet_address:
                    asyncio.create_task(self._update_user_transactions(wallet_address.decode() if not query_wallet_address else wallet_address,transaction_data))
                    # await asyncio.sleep(2)
                else:
                    return transaction_data
        except Exception as e:
            print(f'There is an Issue fetching User wallet {wallet_address} Transactions Isue:{e}')

    async def _update_user_transactions(self,wallet_address:str,transaction_data:list)->None:
        print('Updating Db with Transaction Data')
        """
        Update user Transaction into db
        """
        try:
            if not transaction_data:
                return 
        
            store_id = "transactions"
            update_collection = self.mongo['User_Transaction']
            update_collection.update_one(
                {"_id":f"{store_id}"},
                {
                    "$set":{
                        f"{wallet_address}":transaction_data,
                        'updated_at':datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f'There is error Updating wallet {wallet_address} Transactions.Issue:{e}')
        
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
    
    
    
            
