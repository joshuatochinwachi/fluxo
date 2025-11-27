import ast
import asyncio
from datetime import datetime
import json
from re import S
from core.config import get_redis_connection
from core.pubsub.channel_manager import ChannelNames

class automation_agent:
    def __init__(self):
        self.redis_db = get_redis_connection()

    # Receives final portfolio data from portfolio_agent
    async def Receive_automation_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.AUTOMATION.value)

        async for message in pubsub.listen():
            try:
                if message['type'] != 'message':
                    print('No  Data')
                    continue
                data = message['data']
                print(f"Received automation data: {data}")

                asyncio.create_task( self._digest_auto(data))
                # Process the automation data as needed

                """"
                    Automation logic can be implemented here
                """

                # publish the final automation data to other systems or agents as needed.
                # await self.redis_db.publish('automation_complete_channel', data)
            except:
                pass

    async def _digest_auto(self,data:dict)->dict:
        if not data:
            return 
        
        digest_time =  str(datetime.now())
        data = data.decode('utf-8')
        data = json.loads(data)
        data['digest_time'] = digest_time
        await self.redis_db.rpush('DAILY_DIGEST',json.dumps(data))
        print('Digest Added!')


