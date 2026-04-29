# Backend
FastAPI backend using OpenAI's API with both vLLM and Ollama providers for easy switching between the two.

Note the provider can be WHATEVER base url you decide.

## Structure
`app/main.py` -> where the API logic is registered.

Folders:
- `api`: How requests enter and leave the backend
- `models`: What the data looks like (chat input and requests, lesson data, session data, prompt builders for Chat_Model vs. Feedback_Model)
- `data`: Lesson descriptions and prompts
- `services`: LLM logic (feedback and chat) + game logic for game mechanics and session logic (defining a session)


## LLM Host Setup
Configuration is done via env files. Create two files in the project root:

**`.env.local`** - using a locally served Ollama instance:
```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
AVAILABLE_MODELS=llama3.2:3b,smollm2:360m
DEFAULT_MODEL=llama3.2:3b
```
> With Ollama you can set several and the user can choose between them. VLLM is bound to one LLM at a time. Make sure you have downloaded the models you specify with ollama pull!

**`.env.prod`** — grabbing a vLLM server instance (hosted by Nvidia DGX at Aarhus University)
```ini
LLM_PROVIDER=vllm
VLLM_BASE_URL=https://your-server.dk/v1
AVAILABLE_MODELS=google/gemma-4-26B-A4B-it
```

> Make sure the model you set as `DEFAULT_MODEL` is actually downloaded and running in Ollama or vLLM before starting.

## Run
WHen you have set up `.env.local` and `.env.prod`, you can run these two
```bash
make dev   # runs locally with .env.local
make prod  # runs locally but fetches url from .env.prod
```

> Both these run local APIs that aren't exposed to the internet. This is intentional since both the frontend and backend live on a server together. The only differences is whether the INFERENCE server that the FastAPI is grabbing is from an external server or locally hosted.