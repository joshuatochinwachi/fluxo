import asyncio
import time
import uuid
import aiohttp
from typing import Dict, Any
from datetime import datetime
from core.config import Settings


class ExternalService:
    def __init__(self):
        self.settings = Settings()


    async def dex_screener_price_data(self,token_address:str)->Dict[str,Any]|None:
        if not isinstance(token_address,str):
            return 
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if not result:
                        return
                    
                    pair_data = result.get('pairs',[])
                    if not pair_data:
                        return
                    
                    pairs_data_info = pair_data[0]
                    price = pairs_data_info.get('priceUsd',0)
                    price_change_1hr = pairs_data_info.get('priceChange').get('h1')

                    price_info:Dict[str,Any] = {
                        'price':price,
                        'price_change_1hr':price_change_1hr
                    }
                    return price_info

    
    async def Apitube_new(self):
        url = ''
        header = {
            'X-API-Key': self.settings.apitube_news
        }
        async with aiohttp.ClientSession() as session:
            async with session.get() as response:
                pass


    async def Coindesk_news(self,limit:int=10):
        url = f'https://data-api.coindesk.com/news/v1/article/list?lang=EN&limit={limit}'
        headers = {
            'X-API-Key': self.settings.coindesk_news
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    news_datas = result.get('Data',[])
                    if not news_datas:
                        return {}
                    
                    news = [
                        {
                            "id":str(uuid.uuid4()),
                            "title": nw.get('TITLE'),
                            "summary": nw.get('BODY','')[:200] + ".....",
                            "url": nw.get('URL','https://...'),
                            'source': nw.get('SOURCE_DATA',{}).get('URL','https://coindesk.com'),
                            'published_at': datetime.fromtimestamp(int(nw.get('PUBLISHED_ON',{int(time.time())}))).strftime("%Y-%m-%d %H:%M:%S"),
                            'relevance': 0.9,
                            'categories': [ ct.get('CATEGORY') for ct in nw.get('CATEGORY_DATA',{}) if ct][:5],
                            'tags': [ 'cyrpto New']

                        }
                        for nw in news_datas if nw 
                    ]
                    # print(news)
                    return news
                else:
                    print(response.status)

