import aiohttp

from core.config import DEFILLAMA_URL_ENDPOINTS


async def _fetch_all_mantle_protocols_data(session)->dict:
    async with session.get(DEFILLAMA_URL_ENDPOINTS['protocols']) as response:
        if response.status != 200:
            raise Exception(f"Error fetching protocols data: {response.status}")
        protocols_data = await response.json()
        return protocols_data
        
        
# Fetch protocols on Mantle chain
async def fetch_protocol_data()->dict:
    async with aiohttp.ClientSession() as session:
        protocols_datas = await _fetch_all_mantle_protocols_data(session)
        if not protocols_datas:
            raise Exception("No protocols data found")
       
        mantle_protocols = []
        for data in protocols_datas:
            if 'Mantle' in data['chains']:
                protocol_data = {
                    'name': data.get('name'),
                    'slug': data.get('slug'),
                    'chain': data.get('chains'),
                    'tvl': data.get('chainTvls',{}).get('Mantle',0),
                    'category': data.get('category'),
                    'url': data.get('url'),
                    'twitter': data.get('twitter'),
                }
                mantle_protocols.append(protocol_data)
        return mantle_protocols
                


async def _fetch_yield_protocols(session)->dict:
     async with session.get(DEFILLAMA_URL_ENDPOINTS['pools']) as response:
        if response.status != 200:
            raise Exception(f"Error fetching protocols data: {response.status}")
        protocols_datas = await response.json()
        return protocols_datas
       

# Fetch yield protocols on Mantle chain [Entry]
async def fetch_mantle_yield_protocols()->dict:
    async with aiohttp.ClientSession() as session:
        protocols_datas = await _fetch_yield_protocols(session)
        if not protocols_datas:
            raise Exception("No Yield protocols data found")
       
        mantle_yield_protocols = []
        for data in protocols_datas['data']:
            if data['chains'] == 'Mantle':
                protocol_data = {
                    'name': data.get('name'),
                    'project': data.get('project'),
                    'symbol': data.get('symbol'),
                    'tvlUsd': data.get('tvlUsd'),
                    'apy': data.get('apy'),
                    'apyBase': data.get('apyBase'),
                    'apyReward': data.get('apyReward'),
                }
                mantle_yield_protocols.append(protocol_data)
        return mantle_yield_protocols
   