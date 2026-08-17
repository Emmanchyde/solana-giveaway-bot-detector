"""
helius.py - On-Chain Data Extraction (Parallel Optimized)
"""

import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PROJECT_TOKEN_MINT

HELIUS_API_KEY = "YOUR_API_KEY_HERE"
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"


def get_wallet_onchain_metrics(wallet_address: str) -> dict:
    """
    Fetch on-chain data for a wallet.
    Returns balance, tx count, creation date, and token holdings.
    """
    metrics = {
        "balance_sol": 0.0,
        "tx_count": 0,
        "wallet_created": "Unknown",
        "holds_project_token": "Not Checked",
    }

    if not wallet_address or not wallet_address.strip():
        return metrics

    wallet = wallet_address.strip()

    try:
        # ---- 1. SOL Balance ----
        res_bal = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet],
            },
            timeout=5,
        ).json()

        if "result" in res_bal:
            metrics["balance_sol"] = res_bal["result"]["value"] / 1e9

        # ---- 2. Transaction Count + Creation Date ----
        res_sigs = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet, {"limit": 100}],
            },
            timeout=5,
        ).json()

        if "result" in res_sigs:
            sigs = res_sigs["result"]
            metrics["tx_count"] = len(sigs)

            if sigs:
                oldest = sigs[-1]
                block_time = oldest.get("blockTime")
                if block_time:
                    created = datetime.fromtimestamp(block_time)
                    metrics["wallet_created"] = created.strftime("%Y-%m-%d %H:%M:%S")

        # ---- 3. Token Holdings (only if token mint is configured) ----
        if PROJECT_TOKEN_MINT and PROJECT_TOKEN_MINT.strip():
            token_balance = check_specific_token(wallet, PROJECT_TOKEN_MINT.strip())
            if token_balance > 0:
                metrics["holds_project_token"] = "Yes"
            else:
                metrics["holds_project_token"] = "No"

    except Exception:
        pass

    return metrics


def check_specific_token(wallet_address: str, mint_address: str) -> float:
    """
    Check if a wallet holds a specific token by mint address.
    Uses the Helius DAS getTokenAccounts API with owner + mint filter.

    Returns the balance if found, otherwise 0.0.
    """
    try:
        response = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccounts",
                "params": {
                    "owner": wallet_address,
                    "mint": mint_address,
                    "limit": 1,
                },
            },
            timeout=5,
        ).json()

        if "result" in response:
            token_accounts = response["result"].get("token_accounts", [])
            if token_accounts:
                amount = token_accounts[0].get("amount", 0)
                return amount / 1e9  # Adjust decimals if needed

    except Exception:
        pass

    return 0.0


def analyze_wallets_onchain(participants):
    """
    Enrich all participants with on-chain data using parallel threads.
    """
    if PROJECT_TOKEN_MINT and PROJECT_TOKEN_MINT.strip():
        print(f"\n🌐 Extracting On-Chain Metrics via Helius (parallel)...")
        print(f"   🔍 Token check ENABLED for mint: {PROJECT_TOKEN_MINT}")
    else:
        print(f"\n🌐 Extracting On-Chain Metrics via Helius (parallel)...")
        print(f"   ⏭️ Token check DISABLED (set PROJECT_TOKEN_MINT in config.py)")

    # Build mapping from wallet to list of participants
    wallet_map = {}
    for p in participants:
        if p.wallet and p.wallet.strip():
            wallet = p.wallet.strip()
            if wallet not in wallet_map:
                wallet_map[wallet] = []
            wallet_map[wallet].append(p)

    unique_wallets = list(wallet_map.keys())
    total = len(unique_wallets)

    if total == 0:
        print("⚠️ No valid wallets to check.")
        return

    print(f"   Fetching data for {total} unique wallets (max_workers=5)...")

    cache = {}
    processed = 0

    # Parallel fetch using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_wallet = {
            executor.submit(get_wallet_onchain_metrics, wallet): wallet
            for wallet in unique_wallets
        }

        # Process results as they complete
        for future in as_completed(future_to_wallet):
            wallet = future_to_wallet[future]
            try:
                data = future.result()
                cache[wallet] = data
            except Exception as e:
                print(f"   ⚠️ Error fetching {wallet}: {e}")
                cache[wallet] = {
                    "balance_sol": 0.0,
                    "tx_count": 0,
                    "wallet_created": "Unknown",
                    "holds_project_token": "Not Checked",
                }

            processed += 1
            if processed % 10 == 0:
                print(f"   Processed {processed}/{total} wallets...")

    # Apply cached data to participants
    for wallet, participants_list in wallet_map.items():
        data = cache.get(wallet, {})
        for p in participants_list:
            p.sol_balance = data.get("balance_sol", 0.0)
            p.tx_count = data.get("tx_count", 0)
            p.wallet_created = data.get("wallet_created", "Unknown")
            p.holds_project_token = data.get("holds_project_token", "Not Checked")

    print(f"✅ On-chain data extracted for {total} unique wallets (parallel complete).")