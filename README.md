# Backend
FastAPI backend using OpenAI's API but with both vLLM and Ollama providers to enable easy switching between the two.

## Structure
Mina's notes: How to structure a backend API

app/main.py -> where the API logic is registered.

Folders:
- API: How requests enter and leave backend
- Models: What the data looks like (chat input and requests, lesson data, session data, prompt builders for Chat_Model vs. Feedback_Model)
- Services: LLM logic (feedback and chat) + game logic for game mechanics and session logic (defining a session)
- Data: Lesson descriptions and prompts are here !

## Current Setup
Define two `env` files for diff. setups. Locally, I recommend `.env.local`which has
```

```

With `make` to develop on the local computer, run: 
```
make dev
```

With `make` to serve on server (DGX), run: 
```
make prod
```