"""
scoring.py

Main risk scoring engine.
"""

from config import (
    LOW_RISK_MAX,
    MEDIUM_RISK_MAX,
)

from heuristics import (
    detect_duplicate_handles,
    detect_multiple_wallets_per_handle,
    detect_short_comments,
    detect_bursts,
    apply_verified_bonus,
)

from wallet import (
    detect_wallet_reuse,
    detect_invalid_wallets,
)

from similarity import (
    detect_duplicate_comments,
    detect_similar_comments,
)


class RiskEngine:

    def __init__(self, participants):

        self.participants = participants

    # -----------------------------------

    def run(self):

        print("Running wallet analysis...")

        detect_invalid_wallets(self.participants)
        detect_wallet_reuse(self.participants)

        print("Running comment analysis...")

        detect_duplicate_comments(self.participants)
        detect_similar_comments(self.participants)

        print("Running thread heuristics...")

        detect_duplicate_handles(self.participants)
        detect_short_comments(self.participants)
        detect_bursts(self.participants)

        print("Applying bonuses...")

        apply_verified_bonus(self.participants)
        print("Running multi-wallet detection...")
        detect_multiple_wallets_per_handle(self.participants)

        print("Finalizing scores...")

        self.finalize()

        return self.participants

    # -----------------------------------

    def finalize(self):

        for p in self.participants:

            # Clamp score

            if p.risk_score < 0:
                p.risk_score = 0

            if p.risk_score > 100:
                p.risk_score = 100

            # Risk Level

            if p.risk_score <= LOW_RISK_MAX:

                p.risk_level = "LOW"

            elif p.risk_score <= MEDIUM_RISK_MAX:

                p.risk_level = "MEDIUM"

            else:

                p.risk_level = "HIGH"

    # -----------------------------------

    def summary(self):

        low = 0
        medium = 0
        high = 0

        for p in self.participants:

            if p.risk_level == "LOW":
                low += 1

            elif p.risk_level == "MEDIUM":
                medium += 1

            else:
                high += 1

        return {

            "participants": len(self.participants),

            "low": low,

            "medium": medium,

            "high": high
        }

    # -----------------------------------

    def highest_risk(self, top=10):

        return sorted(

            self.participants,

            key=lambda p: p.risk_score,

            reverse=True

        )[:top]