from dataclasses import dataclass


@dataclass
class ProtocolData:
    name:str
    slug:str
    chain:str
    tvl:float
    category:str
    url:str
    twitter:str

@dataclass
class YieldlProtocol:
    project:str
    symbol:str
    tvlUsd:float
    apy:float
    apyBase:float
    apyReward:float

@dataclass
class UserPortfolio:
    user_address:str
    token_address:str
    token_symbol:str
    balance: float
    value_usd:float
    price_usd: float
    percentage_of_portfolio:float

@dataclass
class TokenData:
    token:str

@dataclass
class TokenBalance:
    balance:float
