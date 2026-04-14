import ollama
import requests

res = requests.post("http://localhost:8000/chat", json={"message": "Hello"})

print(res.json())
