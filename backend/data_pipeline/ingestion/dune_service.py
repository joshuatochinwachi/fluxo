from urllib import response
import aiohttp
from typing import List

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
            'chain_ids':5000 # Mantle chain Id
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
    async def user_portfolio_analysis(self,user_address:str)->List:
        """
        analyse the portolio of an address 

        Args:
            wallet addresss
        
        return:
            List(Dict)

        """
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

    # fetch token data
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
                    return self._parse_token_data(data,token_address)
        except:
            return None
        
    def _parse_token_data(self,token_data:dict,token_address:str)->dict:
        
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
    
    async def user_transactions(self, wallet_address:str):
        url = DUNE_SERVICE_ENDPOINTS['transaction'] + f"/{wallet_address}"
        headers = {
            "X-Sim-Api-Key":self.settings.dune_api_key
        }
        params = {
            'chain_ids':5000,  #  Mantle Chain ID,
            'decode': 'true'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers,params=params) as response:
                if response.status != 200:
                    return 
                
                result = await response.json()
                parsed_transaction =  await self._parse_transaction(result)
                return parsed_transaction


    async def _parse_transaction(self,trx_data:dict):
        if not trx_data:
            return 
        
        decoded_transaction = []
        for index ,tx in enumerate(trx_data['transactions']):
            if tx.get('chain') != 'mantle':
                continue
            
            tx_time = tx.get('block_time')
            trx_status = tx.get('success')
            filterd_tx = await self._filter_decodes(tx)
            decoded_transaction.append(
                {
                'transaction_status':trx_status,
                'transaction_time':tx_time,
                'transaction':filterd_tx
                }
                )
            
        return decoded_transaction


    async def _filter_decodes(self,decode_logs:list):
        if not decode_logs:
            return 
        
        tx_logs_mapping = {}
        for log in decode_logs.get('logs'):
            log_mapping = {
                log.get('decoded',{}).get('name','Nan')  : log.get('decoded')
            }
            tx_logs_mapping.update(log_mapping)

        tx_hierachy = [
            'Swap',
            'Approval',
            'Transfer',
            'Deposit'
        ]

        if tx_hierachy[0] in  tx_logs_mapping:
            swap_log_data = tx_logs_mapping[ tx_hierachy[0]]
            decode_data = swap_log_data.get('inputs')
            mapping_swap_info = {
                input_data.get('name') : input_data for input_data in decode_data
            }

            amount_in = mapping_swap_info.get('amount1',{}).get('value')
            amount_out = mapping_swap_info.get('amount0',{}).get('value')

            return {
                'transaction_type':"Token Swap",
                'hash':decode_logs.get('hash'),
                'token':'token',
                'amount_in':amount_in,
                'amount_out':amount_out
            }
        
        
        if tx_hierachy[1] in tx_logs_mapping:
            apporval_log_data = tx_logs_mapping[tx_hierachy[1]]
            decode_data = apporval_log_data.get('inputs')
            mapping_approval_info = {
                input_data.get('name') : input_data for input_data in decode_data
            }

            spender = mapping_approval_info.get('spender',{}).get('value')
            owner = mapping_approval_info.get('owner',{}).get('value')
            amount = mapping_approval_info.get('value',{}).get('value')

            return {
                'transaction_type':'Token Approval',
                'hash':decode_logs.get('hash'),
                'token': 'tokekn',
                'spender':spender,
                'owner':owner,
                'amount':amount
            }
        

        if tx_hierachy[2] in  tx_logs_mapping:
            transfer_log_data = tx_logs_mapping[tx_hierachy[2]]
            decode_data = transfer_log_data.get('inputs')
            mapping_transfer_info = {
                input_data.get('name') : input_data for input_data in decode_data
            }

            sender = mapping_transfer_info.get('sender',{}).get('value')
            recipient = mapping_transfer_info.get('recipient',{}).get('value')
            amount = mapping_transfer_info.get('amount',{}).get('value')

            return {
                'transaction_type':'Token Transfer',
                'hash': decode_logs.get('hash'),
                'sender': sender,
                'receiver':recipient,
                'token': 'token',
                'amount':amount
            }
        
        
        if tx_hierachy[3] in tx_logs_mapping:
            deposit_log_data =  tx_logs_mapping[tx_hierachy[3]]
            decode_data = deposit_log_data.get('inputs')
            mapping_deposit_info = {
                input_data.get('name') : input_data for input_data in decode_data
            }

            amount = mapping_deposit_info.get('amount',{}).get('amount')
            return {
                'transaction_type': 'Token Deposit',
                'amount':amount
            }
        

        return {
            'transaction_type':'Unknown',
            'token':'token',
            'hash':decode_logs.get('hash')
        }


        


            






            


