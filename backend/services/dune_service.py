import aiohttp
from core.config import DUNE_SERVICE_ENDPOINTS
from core.config import Settings
from eth_utils import to_checksum_address


class DuneService:
    def __init__(self):
        self.settings = Settings()

    """
        Use dune sim api to implement portfolio analysis
    """
    async def _fetch_user_token_balaance(self, user_address: str) -> dict:
        user_address = to_checksum_address(user_address)
        url = DUNE_SERVICE_ENDPOINTS['balances'] + f"/{user_address}"
        headers = {
            "X-Sim-Api-Key":self.settings.dune_api_key
        }
        params = {
            'chain_ids':5000
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers,params=params) as response:
                if response.status != 200:
                   return
                data = await response.json()
                if 'balances' not in data:
                    return
                return data['balances']

    # main entryy for porfolio analysis        
    async def user_portfolio_analysis(self,user_address:str)->dict:
        user_address = to_checksum_address(user_address)
        user_token_baLances = await self._fetch_user_token_balaance(user_address)
        if not user_token_baLances:
            return 
        
        # Process and return the analysis data
        token_balance_percentage = self._balance_porfolio_percentage(user_token_baLances)
        user_portfolio = []
        for balance in user_token_baLances:
            token_data = {
                'token_address': balance.get('address'),
                'token_symbol': balance.get('symbol'),
                'balance': int(balance.get('amount',0)) / (10 ** balance.get('decimals', 18)),
                'value_usd': balance.get('value_usd'),
                'price_usd': balance.get('price_usd'),
                'percentage_of_portfolio': token_balance_percentage.get(balance.get('address'),0)
            }
            user_portfolio.append(token_data)
        return user_portfolio
    
    def _balance_porfolio_percentage(self,user_token_balances: list[dict]) -> dict:
        total_value = sum(token_balance_data.get('value_usd',0) for token_balance_data in user_token_balances )
        if total_value == 0:
            return { token_balance_data['address']: 0 for token_balance_data in user_token_balances}

        token_porforlio_percentage = {}
        for token_balance_data in user_token_balances:
            percentage = (token_balance_data.get('value_usd',0) * 100) / total_value 
            token_porforlio_percentage.update({token_balance_data['address']: percentage})
        return token_porforlio_percentage


    async def token_data(self, token_address: str) -> dict:
        token_address = to_checksum_address(token_address)
        url = DUNE_SERVICE_ENDPOINTS['token_info'] + f"/{token_address}"
        headers = {
            "X-Sim-Api-Key":self.settings.dune_api_key
        }
        params = {
            'chain_ids':5000  #  Mantle Chain ID
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=headers,params=params) as response:
                    if response.status != 200:
                        return
                    data = await response.json()
                    return data
        except:
            return None