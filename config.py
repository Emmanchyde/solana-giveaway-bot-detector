"""
SybilClean Configuration
"""

# ===============================
# Risk Thresholds
# ===============================

LOW_RISK_MAX = 29
MEDIUM_RISK_MAX = 59

# ===============================
# Risk Weights
# ===============================

RISK_WEIGHTS = {
    # Wallet Rules
    "duplicate_wallet": 80,
    "single_account_wallet_repeat": 10,
    "invalid_wallet": 25,
    "multiple_wallets_same_handle": 15,

    # Handle Rules
    "duplicate_handle": 20,
    "suspicious_handle": 10,

    # Comment Rules
    "duplicate_comment": 5,
    "similar_comment": 5,
    "very_short_comment": 5,

    # Time Rules
    "burst_posting": 20,

    # Bonus / Reductions
    "verified_account": -10,
}

# ===============================
# Dynamic Scaling Parameters
# ===============================

DUPLICATE_HANDLE_STEP_PENALTY = 10

# ===============================
# Similarity Threshold
# ===============================

COMMENT_SIMILARITY = 90

# ===============================
# Burst Detection
# ===============================

BURST_WINDOW_SECONDS = 30
BURST_THRESHOLD = 15

# ===============================
# Wallet Validation
# ===============================

SOLANA_MIN_LENGTH = 32
SOLANA_MAX_LENGTH = 44

BASE58_ALPHABET = (
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    "abcdefghijkmnopqrstuvwxyz"
)

# ===============================
# Wallet Blacklist (Burn / Placeholders)
# ===============================

BLACKLISTED_WALLETS = {
    "11111111111111111111111111111111",
    "So11111111111111111111111111111111111111112",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
}

# ===============================
# Project Token (Optional)
# ===============================
# Set this to your project's token mint address.
# If left empty, the token check is skipped entirely.
# Example: "So11111111111111111111111111111111111111112" (Wrapped SOL)
PROJECT_TOKEN_MINT = "9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump"# <-- USER SETS THIS