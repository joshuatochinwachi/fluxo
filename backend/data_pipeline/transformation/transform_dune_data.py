from typing import List
from ..schemas.data_schemas import UserPortfolio,Transaction

def transform_user_portfolio(user_portfolio_data:List,wallet_address)->List[UserPortfolio]|None:
    if not user_portfolio_data:
        return None
        
    transformed_portfolio_data = []
    for token_balance in user_portfolio_data:
        try:
            transformed_portfolio_data.append(UserPortfolio(
                user_address=wallet_address,
                token_address=token_balance.get('token_address'),
                token_symbol=token_balance.get('token_symbol'),
                balance=token_balance.get('balance'),
                value_usd=token_balance.get('value_usd'),
                price_usd=token_balance.get('price_usd'),
                pnl_24h_pct=token_balance.get('pnl_24h_pct'),
                percentage_of_portfolio=token_balance.get('percentage_of_portfolio')
            ))
        except Exception as e:
            print(f"Error transforming token balance data: {e}")
            continue
    
    return transformed_portfolio_data

def transform_user_transaction_data(transaction_data:dict):
    if not transaction_data:
        return 
    return [
        Transaction(
            transaction_status=tx.get('transaction_status'),
            transaction_time=tx.get('transaction_time'),
            transaction=tx.get('transaction')
        )
        for tx in transaction_data
    ]

