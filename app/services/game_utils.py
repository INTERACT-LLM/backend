"""
Wrapper for random choice for 20Q to standardize across chatmodel system prompt and API endpoint, and to allow for deterministic choice based on session_id.
"""

import random

def pick_secret_20Q(vocabulary: list, session_id: str):
    return random.Random(session_id).choice(vocabulary)