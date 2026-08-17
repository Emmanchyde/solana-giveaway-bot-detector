import csv
import os
from datetime import datetime, timezone

import config
from models import Participant
from helius import analyze_wallets_onchain
from scoring import RiskEngine
from reporting import (
    export_all_reports,
    print_summary,
    print_top,
    print_reason_stats,
)
from html_report import generate_html_report


def parse_timestamp(val):
    """
    Robustly parse timestamps (ISO, Unix, or empty).
    Returns a naive UTC datetime to avoid comparison issues.
    """
    if not val or not str(val).strip():
        return datetime.min

    val = str(val).strip()

    # Try Unix timestamp (float)
    try:
        dt = datetime.fromtimestamp(float(val), tz=timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError):
        pass

    # Try ISO format (e.g., "2024-01-01T00:00:00Z")
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            # Convert to UTC and make naive
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        pass

    return datetime.min


def load_csv(filename):
    participants = []

    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            handle = (
                row.get("Handle") or row.get("handle") or row.get("Username") or ""
            )
            wallet = (
                row.get("Wallet") or row.get("wallet") or row.get("Address") or ""
            )
            comment = (
                row.get("CommentText")
                or row.get("Comment")
                or row.get("comment")
                or ""
            )
            timestamp_str = (
                row.get("TweetTimestamp")
                or row.get("Timestamp")
                or row.get("timestamp")
                or ""
            )
            verified_str = (
                row.get("IsVerified")
                or row.get("Verified")
                or row.get("verified")
                or "FALSE"
            )
            tweet_url = (
                row.get("TweetURL")
                or row.get("TweetUrl")
                or row.get("url")
                or ""
            )

            dt = parse_timestamp(timestamp_str)
            verified = str(verified_str).strip().lower() in ("true", "1", "yes")

            participant = Participant(
                handle=handle,
                wallet=wallet,
                comment=comment,
                timestamp=dt,
                verified=verified,
            )

            if hasattr(participant, "tweet_url"):
                participant.tweet_url = tweet_url

            participants.append(participant)

    return participants


def main():
    print("\n" + "=" * 60)
    print("SybilClean v2 Audit Engine")
    print("=" * 60)

    possible_paths = [
        "data/sybilclean_deep_data.csv",
        "sybilclean_deep_data.csv",
        "data/sybilclean_deep_data_v2.csv",
        "sybilclean_deep_data_v2.csv",
    ]

    target_file = next((p for p in possible_paths if os.path.exists(p)), None)

    if not target_file:
        print("❌ Error: Could not find target CSV file to analyze.")
        return

    print(f"📂 Analyzing dataset: {target_file}")

    # 1. Load ALL participants
    all_participants = load_csv(target_file)
    print(f"📊 Total Scraped Entries : {len(all_participants)}")

    # 2. Run RiskEngine (Handles all heuristics and scoring cleanly)
    engine = RiskEngine(all_participants)
    engine.run()

    # 3. Analyze Wallets On-Chain (Helius)
    wallet_participants = [p for p in all_participants if p.wallet and p.wallet.strip()]
    if wallet_participants:
        analyze_wallets_onchain(wallet_participants)

    # 4. Export Tiered CSVs
    export_all_reports(all_participants)

    # 5. Generate HTML Dashboard
    print("\n📊 Generating interactive HTML dashboard...")
    generate_html_report(all_participants, "sybilclean_audit_report.html")
    print("✅ HTML report saved as 'sybilclean_audit_report.html'")

    # 6. Output Summary Reports to Terminal
    print_summary(engine)
    print_reason_stats(all_participants)
    print_top(engine)


if __name__ == "__main__":
    main()