"""
Solana wallet validation and analysis.
"""

from collections import defaultdict

from config import (
    BASE58_ALPHABET,
    SOLANA_MIN_LENGTH,
    SOLANA_MAX_LENGTH,
    RISK_WEIGHTS,
    BLACKLISTED_WALLETS,
)


# -------------------------------------------------
# Basic Wallet Validation
# -------------------------------------------------

def is_valid_wallet(wallet: str) -> bool:
    """
    Validate a Solana wallet using
    Base58 format, expected length, and blacklist.
    """

    if not wallet:
        return False

    wallet = wallet.strip()

    # Blacklist check (burn / placeholder addresses)
    if wallet in BLACKLISTED_WALLETS:
        return False

    if len(wallet) < SOLANA_MIN_LENGTH:
        return False

    if len(wallet) > SOLANA_MAX_LENGTH:
        return False

    for c in wallet:
        if c not in BASE58_ALPHABET:
            return False

    return True


# -------------------------------------------------
# Build Wallet Map
# -------------------------------------------------

def build_wallet_index(participants):
    """
    Build:

        wallet -> list of participant objects

    Preserves all submission rows so single-account
    repeated wallet submissions are accurately evaluated.
    """

    wallet_map = defaultdict(list)

    for participant in participants:

        wallet = participant.wallet.strip()

        if not wallet:
            continue

        wallet_map[wallet].append(participant)

    return wallet_map


# -------------------------------------------------
# Duplicate Wallet Detection
# -------------------------------------------------

def detect_wallet_reuse(participants):
    """
    Detect wallet reuse across submissions.
    - Multi-account reuse: Wallet shared across distinct handles (Sybil ring).
    - Single-account repeat: Same handle submitting the same wallet address multiple times.
    """

    wallet_map = build_wallet_index(participants)

    for wallet, entries in wallet_map.items():

        if len(entries) <= 1:
            continue

        unique_handles = sorted({p.handle.strip().lower() for p in entries})

        if len(unique_handles) > 1:
            # Multi-account wallet sharing (Sybil attack)
            reason = (
                f"Wallet shared across "
                f"{len(unique_handles)} accounts: "
                f"{', '.join(unique_handles)}"
            )

            for participant in entries:

                participant.wallet_reuse_count = len(unique_handles)

                participant.add_risk(
                    RISK_WEIGHTS["duplicate_wallet"],
                    reason,
                )

                participant.add_flag("wallet_reuse")

        else:
            # Same handle submitting the same wallet address multiple times
            reason = f"Wallet submitted {len(entries)} times by the same account"

            for participant in entries:

                participant.wallet_reuse_count = len(entries)

                participant.add_risk(
                    RISK_WEIGHTS.get("single_account_wallet_repeat", 20),
                    reason,
                )

                participant.add_flag("single_account_wallet_repeat")


# -------------------------------------------------
# Invalid Wallet Detection
# -------------------------------------------------

def detect_invalid_wallets(participants):

    for participant in participants:

        if is_valid_wallet(participant.wallet):
            continue

        participant.add_risk(
            RISK_WEIGHTS["invalid_wallet"],
            "Invalid Solana wallet format",
        )

        participant.add_flag("invalid_wallet")