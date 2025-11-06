import requests

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

response = requests.get(url)
print(response.json())
