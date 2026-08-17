from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Participant:
    """
    Represents one giveaway participant.

    Every heuristic reads and updates this object.
    """

    # ------------------------
    # Raw CSV Data
    # ------------------------

    handle: str
    wallet: str
    comment: str
    timestamp: datetime
    verified: bool

    # ------------------------
    # On-Chain Metadata (Extracted via Helius)
    # ------------------------

    sol_balance: float = 0.0
    tx_count: int = 0
    wallet_created: str = "Unknown"
    holds_project_token: str = "Not Checked"   # Default: not checked

    # ------------------------
    # Calculated During Audit
    # ------------------------

    risk_score: int = 0

    risk_level: str = "LOW"

    reasons: List[str] = field(default_factory=list)

    flags: List[str] = field(default_factory=list)

    # Used internally
    comment_similarity: float = 0.0

    burst_size: int = 0

    wallet_reuse_count: int = 0

    duplicate_comments: int = 0

    duplicate_handles: int = 0

    # ------------------------
    # Helper Methods
    # ------------------------

    def add_risk(self, points: int, reason: str):
        """
        Add risk points while preventing
        duplicate explanations.
        """

        self.risk_score += points

        if reason not in self.reasons:
            self.reasons.append(reason)

    def add_flag(self, flag: str):
        """
        Store internal flags for reporting.
        """

        if flag not in self.flags:
            self.flags.append(flag)

    def finalize(self, config):
        """
        Convert numerical score into
        LOW / MEDIUM / HIGH.
        """

        # Prevent impossible scores

        self.risk_score = max(0, min(100, self.risk_score))

        if self.risk_score <= config.LOW_RISK_MAX:
            self.risk_level = "LOW"

        elif self.risk_score <= config.MEDIUM_RISK_MAX:
            self.risk_level = "MEDIUM"

        else:
            self.risk_level = "HIGH"