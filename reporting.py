"""
Exports CSVs – only LOW, MEDIUM, HIGH, and WALLETS_WITH_BALANCE.
Invalid / no‑wallet / blacklisted entries are skipped.
"""

import csv
from collections import Counter
from wallet import is_valid_wallet
from config import BLACKLISTED_WALLETS


def export_csv(filename, participants):
    fields = [
        "Handle", "Wallet", "Balance_SOL", "Tx_Count",
        "Wallet_Created", "Holds_Token", "RiskScore", "RiskLevel",
        "Verified", "Timestamp", "Comment", "Reasons"
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in participants:
            writer.writerow({
                "Handle": p.handle,
                "Wallet": p.wallet,
                "Balance_SOL": f"{p.sol_balance:.4f}",
                "Tx_Count": p.tx_count,
                "Wallet_Created": p.wallet_created,
                "Holds_Token": p.holds_project_token,
                "RiskScore": p.risk_score,
                "RiskLevel": p.risk_level,
                "Verified": p.verified,
                "Timestamp": p.timestamp,
                "Comment": p.comment,
                "Reasons": " | ".join(p.reasons),
            })


def export_all_reports(participants):
    low, medium, high, funded = [], [], [], []

    for p in participants:
        # Skip if no wallet, blacklisted, or invalid
        if not p.wallet or not p.wallet.strip():
            continue
        wallet = p.wallet.strip()
        if wallet in BLACKLISTED_WALLETS:
            continue
        if not is_valid_wallet(wallet):
            continue

        # Funded wallets (valid ones)
        if p.sol_balance > 0.0:
            funded.append(p)

        # Risk classification
        if p.risk_level == "LOW":
            low.append(p)
        elif p.risk_level == "MEDIUM":
            medium.append(p)
        else:
            high.append(p)

    export_csv("LOW_RISK.csv", low)
    export_csv("MEDIUM_RISK.csv", medium)
    export_csv("HIGH_RISK.csv", high)
    export_csv("WALLETS_WITH_BALANCE.csv", funded)

    print("\n" + "=" * 60)
    print("CSV Files Generated Successfully")
    print("=" * 60)
    print(f"🟢 LOW_RISK.csv              ({len(low)} entries)")
    print(f"🟡 MEDIUM_RISK.csv           ({len(medium)} entries)")
    print(f"🔴 HIGH_RISK.csv             ({len(high)} entries)")
    print(f"💰 WALLETS_WITH_BALANCE.csv  ({len(funded)} funded entries)")


def unique_handles(participants):
    return {p.handle.strip().lower() for p in participants if p.handle.strip()}


def unique_wallets(participants):
    return {p.wallet.strip() for p in participants if p.wallet.strip()}


def print_summary(engine):
    participants = engine.participants
    low = [p for p in participants if p.risk_level == "LOW"]
    medium = [p for p in participants if p.risk_level == "MEDIUM"]
    high = [p for p in participants if p.risk_level == "HIGH"]
    funded = [p for p in participants if p.sol_balance > 0.0]

    # Count skipped for info
    from wallet import is_valid_wallet
    from config import BLACKLISTED_WALLETS
    skipped = 0
    for p in participants:
        if not p.wallet or not p.wallet.strip() or p.wallet.strip() in BLACKLISTED_WALLETS or not is_valid_wallet(p.wallet):
            skipped += 1

    print()
    print("=" * 60)
    print("              SYBILCLEAN AUDIT REPORT")
    print("=" * 60)
    print()
    print(f"Total Entries          : {len(participants)}")
    print(f"Valid Wallets Analyzed : {len(participants) - skipped}")
    print(f"Skipped (no/invalid wallet) : {skipped}")
    print()
    print(f"Low Risk Entries       : {len(low)}")
    print(f"Medium Risk Entries    : {len(medium)}")
    print(f"High Risk Entries      : {len(high)}")
    print(f"Funded Wallets (>0 SOL): {len(funded)}")
    print()
    print("=" * 60)


def print_top(engine, top=10):
    print()
    print("=" * 60)
    print("TOP RISK PARTICIPANTS")
    print("=" * 60)
    for p in engine.highest_risk(top):
        print()
        print("----------------------------------------")
        print(f"{p.handle}")
        print(f"Risk Score : {p.risk_score}")
        print(f"Risk Level : {p.risk_level}")
        print(f"SOL Balance: {p.sol_balance:.4f}")
        print(f"Tx Count   : {p.tx_count}")
        print()
        print("Evidence")
        for r in p.reasons:
            print(f" • {r}")
        print("----------------------------------------")


def print_reason_stats(participants):
    counts = Counter()
    for p in participants:
        for reason in p.reasons:
            counts[reason] += 1
    print()
    print("=" * 60)
    print("TOP DETECTION REASONS")
    print("=" * 60)
    for reason, total in counts.most_common():
        print(f"{reason:<45}{total}")