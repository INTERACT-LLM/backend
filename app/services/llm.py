"""
Add minimal LLM logic here 
"""
import ollama
MODEL = "smollm:1.7b"
SYSTEM_PROMPT = "You are a helpful assistant."

def generate_reply(message: str) -> str:
    # download the model if not already present
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    )

    return response["message"]["content"]