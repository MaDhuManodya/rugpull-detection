import os
import json
import time
import requests
import pandas as pd
import redis
from dotenv import load_dotenv

load_dotenv()

# Configuration
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

BATCH_SIZE = 100
MAX_RETRIES = 5
BASE_SLEEP = 1 # seconds

RAW_API_DIR = "datasets/raw/api_responses"
os.makedirs(RAW_API_DIR, exist_ok=True)

print("Initializing Phase 2: On-Chain Feature Collection...")

# Connect to Redis Cache
try:
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    cache.ping()
    print("Connected to Redis cache successfully.")
except Exception as e:
    print(f"CRITICAL WARNING: Redis connection failed ({e}). Resumability disabled.")
    cache = None # Fallback memory dict if no redis
    memory_cache = {}

def get_from_cache(address):
    if cache:
        val = cache.get(f"features:{address}")
        return json.loads(val) if val else None
    return memory_cache.get(address)

def set_to_cache(address, data):
    if cache:
        cache.set(f"features:{address}", json.dumps(data))
    else:
        memory_cache[address] = data

def save_raw_response(address, source, response_json):
    filepath = os.path.join(RAW_API_DIR, f"{address}_{source}.json")
    with open(filepath, 'w') as f:
        json.dump(response_json, f, indent=4)

def execute_with_backoff(url, params):
    """Executes a request with exponential backoff on 429."""
    for attempt in range(MAX_RETRIES):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            sleep_time = BASE_SLEEP * (2 ** attempt)
            print(f"Rate limited (429). Sleeping for {sleep_time}s...")
            time.sleep(sleep_time)
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}
    return {"error": "Max retries exceeded"}

def collect_features_for_address(address, chain):
    """Pulls data from Etherscan/BscScan for the given address."""
    if pd.isna(address) or not isinstance(address, str):
        return {"error": "Invalid address"}
    
    if "ETH" in chain.upper() or "ETHEREUM" in chain.upper():
        api_url = "https://api.etherscan.io/api"
        api_key = ETHERSCAN_API_KEY
    elif "BSC" in chain.upper() or "BINANCE" in chain.upper():
        api_url = "https://api.bscscan.com/api"
        api_key = BSCSCAN_API_KEY
    else:
        return {"error": f"Unsupported chain: {chain}"}
    
    if not api_key:
        return {"error": "Missing API Key for " + chain}

    # Fetch ABI/Contract info
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": api_key
    }
    
    source_res = execute_with_backoff(api_url, params)
    save_raw_response(address, "explorer_source", source_res)
    
    if source_res.get("status") == "1":
        return {"status": "success", "data": source_res["result"][0]}
    else:
        return {"error": source_res.get("result", "Unknown API Error")}

def run_collection():
    df = pd.read_csv("datasets/processed/train.csv")
    addresses = df[['token_address', 'chain']].dropna().values.tolist()
    
    total = len(addresses)
    success_count = 0
    fail_count = 0
    skipped_count = 0
    failed_addresses = []
    
    print(f"Starting batched collection for {total} addresses...")
    
    for i in range(0, total, BATCH_SIZE):
        batch = addresses[i:i + BATCH_SIZE]
        print(f"\\nProcessing Batch {i//BATCH_SIZE + 1} ({i}/{total})...")
        
        batch_success = 0
        batch_fail = 0
        
        for address, chain in batch:
            if get_from_cache(address):
                skipped_count += 1
                continue
            
            result = collect_features_for_address(address, chain)
            if "error" in result:
                batch_fail += 1
                fail_count += 1
                failed_addresses.append({"address": address, "reason": result["error"]})
                print(f"Failed [{address}]: {result['error']}")
                df.loc[df['token_address'] == address, 'collection_failed'] = True
            else:
                batch_success += 1
                success_count += 1
                set_to_cache(address, result["data"])
                print(f"Success [{address}]")
            
            # API compliance sleep
            time.sleep(0.2)
            
        print(f"Batch {i//BATCH_SIZE + 1} complete. Success: {batch_success}, Fail: {batch_fail}")
        time.sleep(2) # Backoff between batches
        
    df.to_csv("datasets/processed/train.csv", index=False)
    
    # Export Manifest
    manifest = {
        "total_requested": total,
        "total_success": success_count,
        "total_failed": fail_count,
        "total_skipped_from_cache": skipped_count,
        "failed_addresses": failed_addresses
    }
    with open("datasets/reports/collection_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\\nCollection Complete. Manifest saved. Success: {success_count}, Failed: {fail_count}, Cached: {skipped_count}")

if __name__ == "__main__":
    run_collection()
