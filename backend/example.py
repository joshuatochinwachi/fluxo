import token
import requests
import asyncio

# All Agent Route Url
url = 'https://....../agent/automation'
url = 'https://....../agent/execution'
url = 'https://....../agent/macro'
url = 'https://....../agent/market_data'
url = 'https://....../agent/onchain'
url = 'https://....../agent/portfolio'
url = 'https://....../agent/research'
url = 'https://....../agent/risk'
url = 'https://....../agent/social'
url = 'https://....../agent/x402'
url = 'https://....../agent/yield'


# Agent Response status
url = 'https://....../agent/automation/status/{task_id}'
url = 'https://....../agent/executionstatus/{task_id}'
url = 'https://....../agent/macrostatus/{task_id}'

# response = requests.get(url)
# print(response.json())

# Getting user portfolio analysis

# from services.dune_service import DuneService
# import pandas as pd
# dune_service = DuneService()
# async def main():
#     user_address = '0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64'
#     balance = await dune_service.user_portfolio_analysis(user_address)

#     df = pd.DataFrame(balance)
#     print(df)

# asyncio.run(main())



# from tasks.token_watcher_task.token_listener import TokenListener

# token_listener = TokenListener()
# async def start_token_listener():
#     async for transfer in  token_listener.tranfers_event():
#         print(transfer)

# asyncio.run(start_token_listener())


from tasks.token_watcher_task.token_watcher import TokenWatcher

watch = TokenWatcher()

async def main():
    await watch.watch_transfers()

asyncio.run(main())

