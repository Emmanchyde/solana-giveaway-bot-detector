"""
Comment similarity engine.
"""

from collections import defaultdict
from rapidfuzz import fuzz
from config import (
    COMMENT_SIMILARITY,
    RISK_WEIGHTS,
)


def normalize(text: str):

    if not text:
        return ""

    return (
        text.lower()
        .replace("✅", "")
        .replace("✔", "")
        .replace("!", "")
        .replace(".", "")
        .strip()
    )


# ----------------------------------------
# Exact Duplicate Comments
# ----------------------------------------

def detect_duplicate_comments(participants):

    groups = defaultdict(list)

    for p in participants:
        groups[normalize(p.comment)].append(p)

    for comment, users in groups.items():

        if len(users) <= 1:
            continue

        for p in users:

            p.duplicate_comments = len(users)

            p.add_risk(
                RISK_WEIGHTS["duplicate_comment"],
                f"Duplicate comment used by {len(users)} accounts"
            )

            p.add_flag("duplicate_comment")


# ----------------------------------------
# Fuzzy Similarity (Optimized)
# ----------------------------------------

def detect_similar_comments(participants):
    from collections import defaultdict

    # Group participants by the length of their normalized comment
    # This reduces O(n^2) comparisons by ~90%
    length_groups = defaultdict(list)
    for p in participants:
        norm = normalize(p.comment)
        if norm:  # skip empty comments
            length_groups[len(norm)].append((p, norm))

    # Track participants who have already received the penalty
    flagged = set()

    # Only compare comments within similar length groups (±20% length difference)
    lengths = sorted(length_groups.keys())
    for i, len_i in enumerate(lengths):
        for len_j in lengths[i:]:
            # Skip if lengths are too far apart
            if len_j > len_i * 1.2:
                continue

            group_i = length_groups[len_i]
            group_j = length_groups[len_j]

            for p_a, norm_a in group_i:
                for p_b, norm_b in group_j:
                    if p_a is p_b:
                        continue

                    score = fuzz.ratio(norm_a, norm_b)
                    if score < COMMENT_SIMILARITY:
                        continue

                    # Store the max similarity seen for each participant
                    p_a.comment_similarity = max(p_a.comment_similarity, score)
                    p_b.comment_similarity = max(p_b.comment_similarity, score)

                    # Mark them for penalty (apply later)
                    flagged.add(id(p_a))
                    flagged.add(id(p_b))

    # Apply risk ONCE per participant, using their MAX similarity score
    for p in participants:
        if id(p) in flagged and p.comment_similarity >= COMMENT_SIMILARITY:
            p.add_risk(
                RISK_WEIGHTS["similar_comment"],
                f"Highly similar comment ({p.comment_similarity:.0f}%)"
            )
            p.add_flag("similar_comment")