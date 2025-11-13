from typing import List

from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames
from services.data_pipeline import DataSource

class onchain_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.source = DataSource()

    # Rceives onhain transfer data from (tasks.token_watcher_task.token_watcher.TokenWatcher)
    async def Receive_onchain_transfer(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.ONCHAIN.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received onchain transfer data: {data}")
            # Process the onchain transfer data as needed

            """"
                Whale threshold logic can be implemented here
            """

            # pubslish the whale data to other agents listening.
            await self.redis_db.publish('whale_watch_channel', data)
        
    
    async def protocols(self):
        protocols_data = await self.source.fetch_protocol_data()

        return protocols_data




            