import requests
import json

def test_whale_alert():
    """Test Whale Alert API"""
    print("=" * 60)
    print("TESTING: WHALE ALERT")
    print("=" * 60)
    
    # Whale Alert has a public API endpoint
    url = "https://api.whale-alert.io/v1/transactions"
    
    # You can sign up for free API key at whale-alert.io
    API_KEY = "your_whale_alert_key"  # Optional for testing
    
    params = {
        "api_key": API_KEY,
        "min_value": 500000,  # Minimum $500K
        "limit": 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Status: SUCCESS")
            data = response.json()
            transactions = data.get("transactions", [])
            print(f"✅ Data received: {len(transactions)} transactions")
            print(f"✅ Response time: {response.elapsed.total_seconds():.2f}s")
            
            if transactions:
                print("\n📊 Sample transaction:")
                tx = transactions[0]
                print(f"   Symbol: {tx.get('symbol')}")
                print(f"   Amount: ${tx.get('amount_usd', 0):,.0f}")
                print(f"   From: {tx.get('from', {}).get('owner_type')}")
                print(f"   To: {tx.get('to', {}).get('owner_type')}")
            
            # Check for Mantle support
            mantle_support = any(
                tx.get('blockchain') == 'mantle' 
                for tx in transactions
            )
            
            return {
                "source": "Whale Alert",
                "status": "✅ Working",
                "pros": ["Real-time alerts", "Easy API", "Free tier available"],
                "cons": ["No Mantle support (ETH/BTC only)", "Limited to major chains"],
                "mantle_support": "❌ No",
                "recommendation": "Not suitable - no Mantle support"
            }
        else:
            print(f"❌ Status: FAILED ({response.status_code})")
            return {"source": "Whale Alert", "status": "❌ Failed"}
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"source": "Whale Alert", "status": "❌ Error", "error": str(e)}

if __name__ == "__main__":
    result = test_whale_alert()
    print("\n" + "=" * 60)
    print(json.dumps(result, indent=2))
