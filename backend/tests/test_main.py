

    

# import asyncio
# from web3 import Web3
# from fastapi import FastAPI, BackgroundTasks

# app = FastAPI()

# # 1. Connection Details
# MANTLE_RPC = "https://rpc.testnet.mantle.xyz"
# CONTRACT_ADDRESS = "0x6e522d9c0E3b6Dcf41B8091d32fF009AF176731B"
# CONTRACT_ABI = [
#   {
#     "type": "constructor",
#     "inputs": [],
#     "stateMutability": "nonpayable"
#   },
#   {
#     "name": "logActivity",
#     "type": "function",
#     "inputs": [
#       {
#         "name": "_activity",
#         "type": "string",
#         "internalType": "string"
#       }
#     ],
#     "outputs": [],
#     "stateMutability": "nonpayable"
#   },
#   {
#     "name": "owner",
#     "type": "function",
#     "inputs": [],
#     "outputs": [
#       {
#         "name": "",
#         "type": "address",
#         "internalType": "address"
#       }
#     ],
#     "stateMutability": "view"
#   },
#   {
#     "name": "projectName",
#     "type": "function",
#     "inputs": [],
#     "outputs": [
#       {
#         "name": "",
#         "type": "string",
#         "internalType": "string"
#       }
#     ],
#     "stateMutability": "view"
#   }
# ]
# w3 = Web3(Web3.HTTPProvider(MANTLE_RPC))
# contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# # 2. The Listener Function
# async def log_loop(poll_interval):
#     print("Watching Mantle for trades...")
#     # This filter looks for the 'TradeSimulated' event we created in Remix
#     event_filter = contract.events.TradeSimulated.create_filter(from_block='latest')
#     while True:
#         for event in event_filter.get_new_entries():
#             user = event['args']['user']
#             amount = event['args']['amount']
#             print(f"New Trade Found! User: {user}, Amount: {amount}")
#             # HERE is where you call your existing Python/FastAPI logic
#             # e.g., update_user_db(user, amount)
#         await asyncio.sleep(poll_interval)

# # Start the listener when FastAPI starts
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(log_loop(2))




# ## DEX SIMULATION
# from web3 import Web3
# import time

# # 1. Setup
# ROUTER_ADDRESS = "0x192764A8d669A1C5985055b801D3934399064c12"
# WMNT = "0x675b68aa4d9c2d3bb3f0397048e62e6b7192079c"
# USDT = "0x16568297745778a876a394200673942006739420"

# # Minimal ABI for the Swap function
# ROUTER_ABI = '[{"inputs":[{"uint256":"amountIn","uint256":"amountOutMin","address[]":"path","address":"to","uint256":"deadline"}],"name":"swapExactTokensForTokens","outputs":[{"uint256[]":"amounts"}],"stateMutability":"nonpayable","type":"function"}]'

# @app.post("/simulate-trade")
# async def trade_simulation(amount: int):
#     # This function is called when your contract emits an event
#     # or when your frontend hits this endpoint
    
#     router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)
    
#     # Define the path: WMNT -> USDT
#     path = [WMNT, USDT]
    
#     # Build the transaction
#     # (Make sure your backend wallet has some MNT for gas!)
#     nonce = w3.eth.get_transaction_count(YOUR_BACKEND_WALLET_ADDRESS)
    
#     tx = router.functions.swapExactTokensForTokens(
#         amount * 10**18,  # Amount in (assuming 18 decimals)
#         0,                # Accept any amount of output for simulation
#         path,
#         BACKEND_WALLET_ADDRESS,
#         int(time.time()) + 600
#     ).build_transaction({
#         'from': BACKEND_WALLET_ADDRESS,
#         'nonce': nonce,
#         'gas': 250000,
#         'gasPrice': w3.to_wei('0.05', 'gwei')
#     })

#     signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
#     return {"status": "Trade Sent", "tx_hash": w3.to_hex(tx_hash)}



#     # Minimal ABI specifically for the Approve function for trades 
# ERC20_ABI = '[{"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'

# def approve_token_spending(token_address, spender_address, amount_in_wei):
#     token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    
#     # 1. Build the approval transaction
#     nonce = w3.eth.get_transaction_count(BACKEND_WALLET_ADDRESS)
    
#     tx = token_contract.functions.approve(
#         spender_address, 
#         amount_in_wei
#     ).build_transaction({
#         'from': BACKEND_WALLET_ADDRESS,
#         'nonce': nonce,
#         'gas': 100000,
#         'gasPrice': w3.to_wei('0.05', 'gwei'),
#         'chainId': 5003 # Mantle Sepolia Chain ID
#     })
    
#     # 2. Sign and send
#     signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
#     print(f"Approval Sent! Hash: {w3.to_hex(tx_hash)}")
#     return w3.to_hex(tx_hash)# Minimal ABI specifically for the Approve function for trades 
# ERC20_ABI = '[{"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'

# def approve_token_spending(token_address, spender_address, amount_in_wei):
#     token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    
#     # 1. Build the approval transaction
#     nonce = w3.eth.get_transaction_count(BACKEND_WALLET_ADDRESS)
    
#     tx = token_contract.functions.approve(
#         spender_address, 
#         amount_in_wei
#     ).build_transaction({
#         'from': BACKEND_WALLET_ADDRESS,
#         'nonce': nonce,
#         'gas': 100000,
#         'gasPrice': w3.to_wei('0.05', 'gwei'),
#         'chainId': 5003 # Mantle Sepolia Chain ID
#     })
    
#     # 2. Sign and send
#     signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
#     print(f"Approval Sent! Hash: {w3.to_hex(tx_hash)}")
#     return w3.to_hex(tx_hash)


# import time
# from eth_abi import encode
# from eth_utils import function_signature_to_4byte_selector,to_checksum_address
# from web3 import Web3
# from web3.types import TxParams, Wei

# def simulate_trade_task(amount, address):
#   contract_address='0x1518cC9B50607dA2201805314deB7C3d6A586263'
#   private_key='c3d78f931c98e3b2c6cacf8ee2fddc408230610aa9a0fd0e75d55ddce75215b2'
#   backend_address='0x374eff28C4E01b1E765A1e313FF3efB3125e4972'

#   WMNT = "0xc0eeCFA24E391E4259B7EF17be54Be5139DA1AC7"
#   USDT = "0xa9b72cCC9968aFeC98A96239B5AA48d828e8D827"

#   """
#   Simulate a trade on Mantle DEXs
#   """
#   # try:
      
      
#   print(f'Simulating trade of amount: {amount} to address: {address}')
  
#   w3 = Web3(Web3.HTTPProvider("https://rpc.sepolia.mantle.xyz"))
#   print('connected',w3.is_connected())
  

#   # Define the path: WMNT -> USDT
#   path = [WMNT, USDT]

#   Buy_Token_selector = function_signature_to_4byte_selector("swapExactETHForTokens(uint256,address[],address,uint256)")
  
#   deadline = int(time.time()) + 600
#   amount_in = int(amount * 10**18)
#   amount_out_min = 0
  
#   encoded_params = encode(
#       ["uint256", "address[]", "address", "uint256"],
#       [
#           amount_out_min,
#           [w3.to_checksum_address(token) for token in path],
#           w3.to_checksum_address(address),
#           deadline
#       ]
#   )
  
#   call_data = Buy_Token_selector + encoded_params
#   print(backend_address)
#   nonce = w3.eth.get_transaction_count(backend_address)
#   print(f'Nonce: {nonce}')

  
#   tx = {
#       'from': backend_address,
#       'to': contract_address,
#       'value': w3.to_wei(amount,'ether'),
#       'gasPrice': w3.to_wei('0.05', 'gwei'),
#       'nonce': nonce,
#       'data': call_data,
#       'chainId': 5003 # Mantle Sepolia Chain ID
#   }
  
#   estimated_gas = w3.eth.estimate_gas(tx)
#   print(f'Estimated Gas: {estimated_gas}')
#   tx["gas"] = int(estimated_gas * 1.2)  # 20% buffer

#   signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
#   tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
  
#   return {"status": "Trade Sent", "tx_hash": w3.to_hex(tx_hash)}
#   # except Exception as e:
#   #     print(f'Trade simulation failed: {str(e)}')
        
# amount = 0.5
# address = '0x374eff28C4E01b1E765A1e313FF3efB3125e4972'
# simulate_trade_task(amount, address)




import time
from decimal import Decimal

from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
from web3 import Web3


def simulate_trade_task(amount_eth, recipient):
    # ===== CONFIG =====
    RPC_URL = "https://rpc.sepolia.mantle.xyz"
    CHAIN_ID = 5003

    ROUTER_ADDRESS = Web3.to_checksum_address(
        "0xE82e586Bb270980eb481f06d03b19393655e854F"
    )

    PRIVATE_KEY = "c3d78f931c98e3b2c6cacf8ee2fddc408230610aa9a0fd0e75d55ddce75215b2"
    BACKEND_ADDRESS = Web3.to_checksum_address(
        "0x374eff28C4E01b1E765A1e313FF3efB3125e4972"
    )

    WMNT = Web3.to_checksum_address("0xc0eeCFA24E391E4259B7EF17be54Be5139DA1AC7")
    USDT = Web3.to_checksum_address("0xa9b72cCC9968aFeC98A96239B5AA48d828e8D827")

    # ===== WEB3 =====
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected(), "RPC not connected"

    print("Connected to Mantle Sepolia")

    # ===== ROUTER FUNCTION =====
    # swapExactETHForTokens(uint256,address[],address,uint256)
    selector = function_signature_to_4byte_selector(
        "swapExactETHForTokens(uint256,address[],address,uint256)"
    )

    path = [WMNT, USDT]
    deadline = int(time.time()) + 600  # 10 minutes
    amount_out_min = 0  

    encoded_params = encode(
        ["uint256", "address[]", "address", "uint256"],
        [
            amount_out_min,
            path,
            Web3.to_checksum_address(recipient),
            deadline,
        ],
    )

    call_data = selector + encoded_params

    # ===== TRANSACTION =====
    nonce = w3.eth.get_transaction_count(BACKEND_ADDRESS)

    tx = {
        "from": BACKEND_ADDRESS,
        "to": ROUTER_ADDRESS,
        "value": w3.to_wei(amount_eth, "ether"),
        "data": call_data,
        "gas":22000000000,
        "nonce": nonce,
        "gasPrice": w3.to_wei("1", "gwei"),
        "chainId": CHAIN_ID,
    }

    print("Estimating gas...")
    # estimated_gas = w3.eth.estimate_gas(tx)
    # tx["gas"] = int(estimated_gas * 1.2)

    # print("Estimated gas:", estimated_gas)

    # ===== SIGN & SEND =====
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print("Transaction sent:", w3.to_hex(tx_hash))
    return w3.to_hex(tx_hash)


# ===== RUN =====
# simulate_trade_task(
#     amount_eth="0.5",
#     recipient="0x374eff28C4E01b1E765A1e313FF3efB3125e4972",
# )




def trade_simulation(amount: int):
  
  RPC_URL = "https://rpc.sepolia.mantle.xyz"
  CHAIN_ID = 5003

  ROUTER_ADDRESS = Web3.to_checksum_address(
      "0xE82e586Bb270980eb481f06d03b19393655e854F"
  )
  ABI = [{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
  PRIVATE_KEY = "c3d78f931c98e3b2c6cacf8ee2fddc408230610aa9a0fd0e75d55ddce75215b2"
  BACKEND_ADDRESS = Web3.to_checksum_address(
      "0x374eff28C4E01b1E765A1e313FF3efB3125e4972"
  )

  WMNT = Web3.to_checksum_address("0xc0eeCFA24E391E4259B7EF17be54Be5139DA1AC7")
  USDT = Web3.to_checksum_address("0xa9b72cCC9968aFeC98A96239B5AA48d828e8D827")

  # ===== WEB3 =====
  w3 = Web3(Web3.HTTPProvider(RPC_URL))
  
  router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ABI)
  
  # Define the path: WMNT -> USDT
  path = [WMNT, USDT]
  
  # Build the transaction
  # (Make sure your backend wallet has some MNT for gas!)
  nonce = w3.eth.get_transaction_count(BACKEND_ADDRESS)
  
  tx = router.functions.swapExactTokensForTokens(
      int(amount * 10**18),  # Amount in (assuming 18 decimals)
      0,                # Accept any amount of output for simulation
      path,
      BACKEND_ADDRESS,
      int(time.time()) + 600
  ).build_transaction({
      'from': BACKEND_ADDRESS,
      'nonce': nonce,
      'gas': 250000,
      'gasPrice': w3.to_wei('0.05', 'gwei')
  })

  signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
  tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
  
  print( {"status": "Trade Sent", "tx_hash": w3.to_hex(tx_hash)})

trade_simulation(0.5)