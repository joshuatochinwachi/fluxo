"""
Execution Agent Celery Task - With Alert Triggering
"""
import asyncio
import json
import time
from core import celery_app
from web3 import Web3
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector,to_checksum_address
from web3.types import TxParams, Wei


@celery_app.task(bind=True, name="execution_preview")
def execution_task(self, wallet_address: str, rebalance_plan: dict = None, alert_on_slippage: bool = True):
    """
    Generate execution preview with alert triggering
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Generating execution preview...', 'progress': 0}
        )
        
        print(f'Generating execution preview for: {wallet_address}')
        
        # Lazy import to avoid circular dependency
        from services.alert_manager import AlertManager
        
        alert_manager = AlertManager()
        
        # Run async execution preview
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Simulating trades on Mantle DEXs...', 'progress': 50}
        )
        
        # Generate execution preview (placeholder)
        # TODO: Implement actual execution preview
        execution_result = {
            'estimated_slippage': 0.5,
            'gas_cost_usd': 2.5,
            'liquidity_depth': 'high'
        }
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking execution alerts...', 'progress': 85}
        )
        
        # Trigger alerts for high slippage (placeholder)
        triggered_alerts = []
        
        loop.close()
        
        print(f'Execution preview completed')
        print(f'Triggered {len(triggered_alerts)} execution alerts')
        
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'execution_preview': execution_result,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'execution',
            'version': '2.0_with_alerts'
        }
    except Exception as e:
        print(f'Execution preview failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'execution'
        }


@celery_app.task(bind=True, name="simulate_trade_task")
def simulate_trade_task(self, amount: int, address: str):
    from core.config import Settings
    settings = Settings()
    MANTLE_RPC = settings.mantle_rpc
    CONTRACT_ADDRESS = settings.contract_address
    PRIVATE_KEY = settings.private_key
    BACKEND_WALLET_ADDRESS = settings.backend_wallet_address
    CONTRACT_ABI = settings.contract_abi

    WMNT = "0xc0eeCFA24E391E4259B7EF17be54Be5139DA1AC7"
    USDT = "0xa9b72cCC9968aFeC98A96239B5AA48d828e8D827"

    """
    Simulate a trade on Mantle DEXs
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Simulating trade...', 'progress': 0}
        )
        
        print(f'Simulating trade of amount: {amount} to address: {address}')
        
        w3 = Web3(Web3.HTTPProvider("https://rpc.sepolia.mantle.xyz"))
        print('connected',w3.is_connected())
        

        # Define the path: WMNT -> USDT
        path = [WMNT, USDT]

        Buy_Token_selector = function_signature_to_4byte_selector("swapEthForExactTokens(uint256,uint256,address[],address,uint256)")[:4]
        
        deadline = int(time.time()) + 600
        amount_in = amount * 10**18
        amount_out_min = 0
        
        encoded_params = encode(
            ["uint256", "uint256", "address[]", "address", "uint256"],
            [
                amount_in,
                amount_out_min,
                [w3.to_checksum_address(token) for token in path],
                w3.to_checksum_address(address),
                deadline
            ]
        )
        
        call_data = Buy_Token_selector + encoded_params
        print(BACKEND_WALLET_ADDRESS)
        nonce = w3.eth.get_transaction_count(BACKEND_WALLET_ADDRESS)
        print(f'Nonce: {nonce}')

        
        tx:TxParams = {
            'from': BACKEND_WALLET_ADDRESS,
            'to': CONTRACT_ADDRESS,
            'value': Wei(amount),
            'gasPrice': w3.to_wei('0.05', 'gwei'),
            'nonce': nonce,
            'data': call_data,
            'chainId': 5003 # Mantle Sepolia Chain ID
        }
        print(tx)
        
        estimated_gas = w3.eth.estimate_gas(tx)
        print(f'Estimated Gas: {estimated_gas}')
        tx["gas"] = int(estimated_gas * 1.2)  # 20% buffer

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {"status": "Trade Sent", "tx_hash": w3.to_hex(tx_hash)}
    except Exception as e:
        print(f'Trade simulation failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'execution'
        }



@celery_app.task(bind=True, name="approve_token_spending_task")
def approve_token_spending_task(self, token_address: str, amount: int, wallet_address: str):
    from core.config import Settings
    settings = Settings()       
    MANTLE_RPC = settings.mantle_rpc
    PRIVATE_KEY = settings.private_key
    BACKEND_WALLET_ADDRESS = settings.backend_wallet_address
    CONTRACT_ADDRESS = settings.contract_address

    w3 = Web3(Web3.HTTPProvider("https://rpc.testnet.mantle.xyz"))
    try:
        # Selector for approve(address,uint256)
        approve_selector = function_signature_to_4byte_selector("approve(address,uint256)")
        
        amount_wei = amount * 10**18
        
        encoded_params = encode(
            ["address", "uint256"],
            [
                to_checksum_address(CONTRACT_ADDRESS),
                amount_wei
            ]
        )
        
        call_data = approve_selector + encoded_params
        
        nonce = w3.eth.get_transaction_count(BACKEND_WALLET_ADDRESS)
        
        tx = {
            'from': BACKEND_WALLET_ADDRESS,
            'to': to_checksum_address(token_address),
            'value': 0,
            'nonce': nonce,
            'gasPrice': w3.to_wei('0.05', 'gwei'),
            'chainId': 5003, # Mantle Sepolia Chain ID
            'data': call_data
        }
        
        estimated_gas = w3.eth.estimate_gas(tx)
        tx["gas"] = int(estimated_gas * 1.2)  # 20% buffer

        # 2. Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return {"status": "Approval Sent", "tx_hash": w3.to_hex(tx_hash)}   
    except Exception as e:
        print(f'Token approval failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'execution'
        }