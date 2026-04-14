import requests
import ollama

res = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Hello"}
)

print(res.json())