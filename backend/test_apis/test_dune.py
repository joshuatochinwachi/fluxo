# backend/test_apis/test_dune.py

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv
API_KEY = os.getenv('DUNE_KEY')

def test_dune():
    """Test Dune Analytics API"""
    print("=" * 60)
    print("TESTING: DUNE ANALYTICS")
    print("=" * 60)
    
    # You need to sign up and get API key first
    # API_KEY = "your_dune_api_key"  # Get from dune.com
    
    # Test with public query
    query_id = "3238044"
    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
    
    headers = {"X-Dune-API-Key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Status: SUCCESS")
            data = response.json()
            rows = data.get("result", {}).get("rows", [])
            print(f"✅ Data received: {len(rows)} records")
            print(f"✅ Response time: {response.elapsed.total_seconds():.2f}s")
            
            if rows:
                print("\n📊 Sample data:")
                print(json.dumps(rows[0], indent=2)[:200] + "...")
            
            return {
                "source": "Dune Analytics",
                "status": "✅ Working",
                "pros": ["Flexible SQL queries", "Mantle support", "Good docs"],
                "cons": ["Rate limits (free tier)", "Slow queries (30s-2min)"],
                "recommendation": "Primary source"
            }
        else:
            print(f"❌ Status: FAILED ({response.status_code})")
            print(f"Error: {response.text}")
            return {"source": "Dune Analytics", "status": "❌ Failed", "error": response.text}
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"source": "Dune Analytics", "status": "❌ Error", "error": str(e)}

if __name__ == "__main__":
    result = test_dune()
    print("\n" + "=" * 60)
    print(json.dumps(result, indent=2))
