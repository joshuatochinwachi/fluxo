import ast
import time
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


# from tasks.token_watcher_task.token_watcher import TokenWatcher

# watch = TokenWatcher()

# async def main():
#     await watch.watch_transfers()

# asyncio.run(main())

# import requests

# url = "http://0.0.0.0:8000/agent/portfolio/?address=0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64"

# response = requests.get(url)
# print(response.status_code)
# print(response.json())


# from data_pipeline.pipeline import Pipeline

# async def main():
#     pipeline = Pipeline()
#     data = await pipeline.user_portfolio('0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64')

# asyncio.run(main())


# from core.config import MONGO_CONNECT

# update_collection = MONGO_CONNECT['Yield_Protocol']
# store_id = "Mantle_yield_protocol"

# data = update_collection.find_one({"_id":store_id})
# print(data)


# from tasks.agent_tasks.macro_task import macro_task

# result = macro_task("0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64")
# print(result)


async def main():
    
    from agents.orchestrator import AlertOrchestrator

    
    event = {
        'token':'0x375450706cb79aB749EBB90001bDa10341dD82BC',
        "amount_usd" : 20000000,
        "from_address" :  '0xkksdi',
        "to_address" : '0Xwdhdjjsa',
        "transaction_hash" :  'ioiqnas',
        "symbol" : 'MNT',
        "block_number" :  12344
    }
    smart_money = AlertOrchestrator()
    await smart_money.process_event(event)

# asyncio.run(main())


# from services.llm_providers import LLMClient

# prompt = (
#         f"Market: price_change=300% ; "
#         f"Social: spike=300% ; "
#         f"Manipulation risk=50% ; \n"
#         f"Write a one-sentence analyst summary describing the situation for token ETH."
#         )


# async def main():
#     lm = LLMClient()
#     lm.Call_gemini(prompt)

# asyncio.run(main())

# message = (
#     f"Top  yield opportunities found:\n" +
#     "\n" +'hell' +
#     f"\nConsider diversifying across these protocols for optimal returns."
# )
# print(message)

# from tasks.agent_tasks import risk_task

# risk_task('0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64',)


# from data_pipeline.ingestion.dune_service import DuneService

# dune = DuneService()

# async def main():
#     await dune.user_transactions('0xD51465F03622bAC36D391Ec752561F4516424C05')

# asyncio.run(main())

# from data_pipeline.ingestion.mantle_api import MantleAPI
# mantle = MantleAPI()


from agents.portfolio_agent import portfolio_agent

pipe = portfolio_agent()

async def main():
    data  = await pipe.analyze_portfolio('0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64')
    print(data)
asyncio.run(main())