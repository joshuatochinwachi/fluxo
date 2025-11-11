from web3 import Web3,AsyncHTTPProvider
from eth_utils import to_checksum_address

from core.config import MANTLE_RPC_URL

# Initialize Web3 instance for Mantle network
w3_mantle = Web3(AsyncHTTPProvider(MANTLE_RPC_URL))

class MantleAPI:
    def __init__(self):
        self.web3 = w3_mantle

    async def get_balance(self, address: str) -> float:
        """Fetch the balance of an address on the Mantle network."""
        checksum_address = to_checksum_address(address)
        balance_wei = await self.web3.eth.get_balance(checksum_address)
        balance_eth = self.web3.fromWei(balance_wei, 'ether')
        return balance_eth
    
    async def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """Fetch the ERC20 token balance of a wallet on the Mantle network."""
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

