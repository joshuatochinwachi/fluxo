# backend/test_apis/test_flipside.py

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv
API_KEY = os.getenv('FLIPSIDE_KEY')

def test_flipside():
    """Test Flipside Crypto API"""
    print("=" * 60)
    print("TESTING: FLIPSIDE CRYPTO")
    print("=" * 60)
    
    # Flipside API endpoint
    # Sign up at flipsidecrypto.xyz for API key
    # API_KEY = "your_flipside_key"
    
    url = "https://api-v2.flipsidecrypto.xyz/json-rpc"
    
    # Test query
    query = """
    SELECT 
        tx_hash,
        from_address,
        to_address,
        amount_usd
    FROM ethereum.core.fact_transactions
    WHERE amount_usd > 1000000
    LIMIT 5
    """
    
    payload = {
        "jsonrpc": "2.0",
        "method": "createQuery",
        "params": {
            "sql": query,
            "ttlMinutes": 10
        },
        "id": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Status: SUCCESS")
            data = response.json()
            print(f"✅ Query created")
            print(f"✅ Response time: {response.elapsed.total_seconds():.2f}s")
            
            # Check for Mantle support in their docs
            return {
                "source": "Flipside Crypto",
                "status": "✅ Working",
                "pros": ["SQL queries", "Good documentation", "Community queries"],
                "cons": ["Mantle support unclear", "Need to verify chain support"],
                "mantle_support": "⚠ Unknown - needs verification",
                "recommendation": "Backup option - verify Mantle support first"
            }
        else:
            print(f"❌ Status: FAILED ({response.status_code})")
            return {"source": "Flipside Crypto", "status": "❌ Failed"}
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"source": "Flipside Crypto", "status": "❌ Error", "error": str(e)}

if __name__ == "__main__":
    result = test_flipside()
    print("\n" + "=" * 60)
    print(json.dumps(result, indent=2))
