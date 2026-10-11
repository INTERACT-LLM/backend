"""
Wrapper for random choice for 20Q to standardize across chatmodel system prompt and API endpoint.
Deterministic: the same seed (the chat_id) always picks the same word, so the prompt and the UI agree.
"""

import random

def pick_secret_20Q(vocabulary: list, seed: str): 
    return random.Random(seed).choice(vocabulary)