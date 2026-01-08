from datetime import datetime
import logging
import aiohttp
from typing import List,Optional,AsyncIterator
from aiohttp import ClientSession as session
from pydantic import BaseModel

from web3 import Web3,AsyncHTTPProvider,AsyncWeb3,WebSocketProvider
from eth_utils import to_checksum_address
from eth_abi import decode
from eth_abi.exceptions import InsufficientDataBytes

from core.config import MANTLE_RPC_URL,MANTLE_WSS_URL, Settings

logger = logging.getLogger(__name__)

class TranferReponse(BaseModel):
    token: str
    from_address: str
    to_address: str
    amount: int
    transaction_hash: str
    block_number: int

class MantleAPI:
    def __init__(self):
        transfer_event_signature = "Transfer(address,address,uint256)"
        self.tranfer_topic = [ AsyncWeb3.keccak(text=transfer_event_signature)]
        self.subscription_id : Optional[str] = None
        self.w3 = None
        self.web3 = AsyncWeb3(AsyncHTTPProvider(MANTLE_RPC_URL))
        self.settings =  Settings()

    # Fetch MNT user balance
    async def get_balance(self, address: str) -> float:
        """Fetch the balance of an address on the Mantle network."""
        checksum_address = to_checksum_address(address)
        balance_wei = await self.web3.eth.get_balance(checksum_address)
        balance_eth = self.web3.fromWei(balance_wei, 'ether')
        return balance_eth
    
    # fetch user token balance
    async def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """
        Fetch the ERC20 token balance of a wallet on the Mantle network.
        """
        checksum_token_address = to_checksum_address(token_address)
        checksum_wallet_address = to_checksum_address(wallet_address)
        
        # ERC20 Token ABI (only the balanceOf function)
        erc20_abi = [
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
        ]
        
        token_contract = self.web3.eth.contract(address=checksum_token_address, abi=erc20_abi)
        balance = await token_contract.functions.balanceOf(checksum_wallet_address).call()
        decimals = await token_contract.functions.decimals().call()
        adjusted_balance = balance / (10 ** decimals)
        return adjusted_balance


    # Listen to tokens Transfer Events
    async def tranfers_event(self) -> AsyncIterator[dict]:
        """"
        This function get all the token transfer happening in mantle Network
        
        return:
            AsyncIterato[dict]
            TranferReponse(
                token=to_checksum_address(log.get("address")),
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                transaction_hash= "0x" + log.get("transactionHash").hex(),
                block_number=log.get("blockNumber")
            )
        """
        async with AsyncWeb3(WebSocketProvider(MANTLE_WSS_URL)) as w3:
            self.w3 = w3

            params = {
                "address": None,
                "topics": self.tranfer_topic
            }
            self.subscription_id = await w3.eth.subscribe("logs", params)
            print(f"Subscribed to Transfer events with subscription ID: {self.subscription_id}")

            async for payload in w3.socket.process_subscriptions():
                if payload.get("subscription") != self.subscription_id:
                        continue
                        
                log = payload.get("result")
                if not log:
                    continue
                
                # Determine event type from topic0
                topic0 = log.get("topics", [])[0] if log.get("topics") else None
                if not topic0:
                    continue

                if topic0 != self.tranfer_topic[0]:
                    continue

                transfer_event = await self._parse_transfer_event(log)
                if not transfer_event:
                    continue
                yield transfer_event

    # Pasrse Transfer Event Log
    async def _parse_transfer_event(self,log:dict)->TranferReponse|None:
        try:
            topics = log.get("topics", [])
            data = log.get("data", "0x")

            from_address = to_checksum_address("0x" + topics[1].hex()[24:])
            to_address = to_checksum_address("0x" + topics[2].hex()[24:])
            
            if isinstance(data, str):
                data =  bytes.fromhex(data[2:] if data.startswith('0x') else data)
        
            amount = decode(['uint256'], data)[0]
            return TranferReponse(
                token=to_checksum_address(log.get("address")),
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                transaction_hash= "0x" + log.get("transactionHash").hex(),
                block_number=log.get("blockNumber")
            )
        except InsufficientDataBytes as e:
            logger.error(f"Error decoding event data: {e}")
            return None
    
    async def _normal_transactions(self,wallet_address:str,session:session)->None|dict:
        print(f'Fetching Normal Transaction For Wallet {wallet_address}')
        """
            This gets the normal transaction made by the user wallet
        """
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid":'5000',
            "action":"txlist",
            "address":wallet_address,
            "startblock":0,
            "sort":"desc",
            "apikey":self.settings.etherscan,
            "module":"account"
        }
        async with session.get(url=url, params=params) as response:
            if response.status != 200:
                return 
            
            result =  await response.json()
            if not result:
                return 
            if not  (
                tx_results := result.get('result')
            ):
                return 
            
            tx_mapping = {
                tx.get('hash') : {
                    'tx_hash':tx.get('hash'),
                    "from":tx.get('from'),
                    "to":tx.get('to'),
                    'value':tx.get('value'),
                    'gas_used':tx.get('gasUsed'),
                    "timestamp":tx.get('timeStamp'),
                    'function_name':tx.get('functionName'),
                    'methodId':tx.get('methodId')

                }
                for tx in tx_results if tx
            }
            return tx_mapping
        
    async def _token_transactions(self,wallet_address:str,session:session)->None|dict:
        print(f'Fetching Token Tranasction For Wallet {wallet_address}')
        """
        Get user token transfer transaction
        This usually get the tranfer made when selling token
        """
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid":'5000',
            "action":"tokentx",
            "address":wallet_address,
            "startblock":0,
            "sort":"desc",
            "apikey":self.settings.etherscan,
            "module":"account"
        }


        async with session.get(url=url, params=params) as response:
            if response.status != 200:
                return 
            
            result =  await response.json()
            if not result:
                return 
            if not  (
                tx_results := result.get('result')
            ):
                return 
            
            tx_mapping = {
                tx.get('hash') : {
                    'tx_hash':tx.get('hash'),
                    "from":tx.get('from'),
                    "to":tx.get('to'),
                    'value':tx.get('value'),
                    'gas_used':tx.get('gasUsed'),
                    "timestamp":tx.get('timeStamp'),
                    'function_name':tx.get('functionName'),
                    "contract_interacted":tx.get('contractAddress'),
                    "value": tx.get('value'),
                    "tokenName": tx.get('tokenName'),
                    "tokenSymbol": tx.get('tokenSymbol'),
                    "tokenDecimal": tx.get('tokenDecimal')
                }
                for tx in tx_results
            }
            return tx_mapping
        
    
    def _aggregate_transactions(self,token_transfers:dict,normal_transactions:dict)->None|dict:
        print(f'Aggregating Transaction For wallet ')
        """
         Combine User normal transaction and the token transfer transactions
        """
        if not token_transfers and not normal_transactions :
            return 
        
        if token_transfers is None:
            token_transfers = {}

        if normal_transactions is None:
            normal_transactions = {}

        transactions = []
        # Get all transaction that are not Token transfer related tx eg (Approval)
        for tx_hash, tx_hash_data in normal_transactions.items():
            if tx_hash in token_transfers:
                continue
            
            normal_tx = {}
            function_name = tx_hash_data.get('function_name')
            txn_name = function_name.split('(',1)[0].strip()

            normal_tx['transaction_name'] = txn_name
            normal_tx['tx_hash'] = tx_hash_data.get('tx_hash')
            normal_tx['from']= tx_hash_data.get('from')
            normal_tx['to'] =  tx_hash_data.get('to')
            normal_tx['value'] =  int(tx_hash_data.get('value',0))/10**18
            normal_tx['transaction_time'] = datetime.fromtimestamp(int(tx_hash_data.get('timestamp',1)))
            
            
            if not txn_name and tx_hash_data.get('methodId') == '0x':
                normal_tx['transaction_name'] = 'Transfer'
                normal_tx['tokenSymbol'] = 'MNT'


            transactions.append(normal_tx)
            # transactions.append({
            #     'transaction_name':txn_name,
            #     'tx_hash':tx_hash_data.get('tx_hash'),
            #     'from':tx_hash_data.get('from'),
            #     'to':tx_hash_data.get('to'),
            #     'value': int(tx_hash_data.get('value',0))/10**18,
            #     'transaction_time':datetime.fromtimestamp(int(tx_hash_data.get('timestamp',1)))
            # })

        for tx_hash_data in token_transfers.values():
            function_name = tx_hash_data.get('function_name')
            txn_name = function_name.split('(',1)[0].strip()

            transactions.append({
                'transaction_name':txn_name,
                'tx_hash':tx_hash_data.get('tx_hash'),
                'tokenSymbol':tx_hash_data.get('tokenSymbol'),
                'value': int(tx_hash_data.get('value',0))/ 10 ** int(tx_hash_data.get('tokenDecimal',18)),
                'from':tx_hash_data.get('from'),
                'to':tx_hash_data.get('to'),
                'contract_interacted':tx_hash_data.get('contract_interacted'),
                'transaction_time':datetime.fromtimestamp(int(tx_hash_data.get('timestamp',1)))
            })
        return transactions[:200] # Get only the first N transactions

    async def user_transactions(self,wallet_address:str)->None|dict:
        """
            Get all the transaction for the wallet Aside internal transaction
        """
        if (not isinstance(wallet_address,str)) or (not wallet_address.startswith('0x')):
            return 
        async with aiohttp.ClientSession() as session:
            token_transactions = await self._token_transactions(
                wallet_address=wallet_address,
                session=session)
            # print(token_transactions)
            normal_transaction = await self._normal_transactions(
                wallet_address=wallet_address,
                session=session
            )
            # print(normal_transaction)

            return  self._aggregate_transactions(
                token_transfers=token_transactions,
                normal_transactions=normal_transaction
            )
            
