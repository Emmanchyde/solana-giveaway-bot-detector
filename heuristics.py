"""
Thread-level heuristics.
"""

from collections import defaultdict
from config import (
    RISK_WEIGHTS,
    DUPLICATE_HANDLE_STEP_PENALTY,
    BURST_WINDOW_SECONDS,
    BURST_THRESHOLD,
)


# ----------------------------------------
# Duplicate Handle Detection
# ----------------------------------------

def detect_duplicate_handles(participants):

    handles = defaultdict(list)

    for p in participants:
        handles[p.handle.lower()].append(p)

    for handle, users in handles.items():

        if len(users) <= 1:
            continue

        extra_comments = len(users) - 1
        base_penalty = RISK_WEIGHTS.get("duplicate_handle", 35)

        # Dynamic scaling: 2 comments = 35 pts (MEDIUM risk), 3 comments = 50 pts, 4+ = 65+ pts (HIGH risk)
        penalty = min(85, base_penalty + ((extra_comments - 1) * DUPLICATE_HANDLE_STEP_PENALTY))

        for p in users:

            p.duplicate_handles = len(users)

            p.add_risk(
                penalty,
                f"Handle commented {len(users)} times"
            )

            p.add_flag("duplicate_handle")


# ----------------------------------------
# Very Short Comments
# ----------------------------------------

def detect_short_comments(participants):

    LOW_VALUE = {
        "done",
        "done!",
        "done ✅",
        "done ✔",
        "gm",
        "ok",
        "yes",
        ".",
        "🔥",
        "✅",
        "✔"
    }

    for p in participants:

        comment = p.comment.lower().strip()

        if comment in LOW_VALUE or len(comment) < 5:

            p.add_risk(
                RISK_WEIGHTS["very_short_comment"],
                "Very short / low-effort comment"
            )

            p.add_flag("short_comment")


# ----------------------------------------
# Timestamp precision detection (for Nitter)
# ----------------------------------------

def _is_low_precision_timestamp(participants):
    """
    Checks if timestamps lack milliseconds/seconds.
    If more than 60% of entries have second=0 and microsecond=0,
    we assume it's Nitter data (minute‑level precision).
    """
    if len(participants) < 5:
        return False

    samples = min(len(participants), 30)
    rounded = 0

    for i in range(samples):
        p = participants[i]
        # Check if timestamp has no seconds or microseconds
        if p.timestamp.second == 0 and p.timestamp.microsecond == 0:
            rounded += 1

    return (rounded / samples) > 0.6


# ----------------------------------------
# Burst Detection
# ----------------------------------------

def detect_bursts(participants):

    if not participants:
        return

    # Auto‑detect low‑precision timestamps (Nitter) and skip burst detection
    if _is_low_precision_timestamp(participants):
        print("ℹ️ Low‑precision timestamps detected (likely Nitter). Skipping burst detection to avoid false positives.")
        return

    participants.sort(key=lambda p: p.timestamp)

    n = len(participants)

    # Store object IDs rather than Participant objects
    # because Participant is not hashable.
    burst_participants = {}

    for i in range(n):

        current = participants[i]
        burst = [current]

        for j in range(i + 1, n):

            other = participants[j]

            delta = (
                other.timestamp -
                current.timestamp
            ).total_seconds()

            if delta > BURST_WINDOW_SECONDS:
                break

            burst.append(other)

        if len(burst) >= BURST_THRESHOLD:

            for user in burst:

                user_id = id(user)

                # Keep the largest burst observed for this user.
                if user_id not in burst_participants:
                    burst_participants[user_id] = user

                user.burst_size = max(
                    user.burst_size,
                    len(burst)
                )

    # Apply burst risk only ONCE per participant.
    for user in burst_participants.values():

        user.add_risk(
            RISK_WEIGHTS["burst_posting"],
            f"Posted during burst of {user.burst_size} replies"
        )

        user.add_flag("burst")


# ----------------------------------------
# Verified Bonus
# ----------------------------------------

def apply_verified_bonus(participants):

    for p in participants:

        if not p.verified:
            continue

        p.add_risk(
            RISK_WEIGHTS["verified_account"],
            "Verified account"
        )


# ----------------------------------------
# Multiple Wallets per Handle (NEW)
# ----------------------------------------

def detect_multiple_wallets_per_handle(participants):
    """Flag accounts that submit multiple unique wallet addresses."""
    handle_wallets = defaultdict(set)

    for p in participants:
        if p.wallet and p.wallet.strip():
            handle_wallets[p.handle.lower()].add(p.wallet.strip())

    for handle, wallets in handle_wallets.items():
        if len(wallets) > 1:
            for p in participants:
                if p.handle.lower() == handle and p.wallet and p.wallet.strip():
                    p.add_risk(
                        RISK_WEIGHTS["multiple_wallets_same_handle"],
                        f"Account submitted {len(wallets)} different wallets"
                    )
                    p.add_flag("multiple_wallets")