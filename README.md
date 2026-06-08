# Backend

FastAPI backend for the [InteractLLM frontend](https://github.com/INTERACT-LLM/frontend). 

Talks to LLMs through the OpenAI-compatible API, with vLLM, Ollama, and Anthropic as supported providers (see configuration below).

## Overview
`app/main.py` is where the API logic is registered. The table below gives an overview of the `app` folder; deeper write-ups for individual subfolders live in their own `README.md`, linked in the "More Info" column.
| 📁 Folder | Description | More Info |
| --- | --- | --- |
| `api` | Request entry and exit points for the backend. | |
| `data` | Lesson definitions and prompt templates. | |
| `models` | Data shapes: chat and feedback payloads, lesson and session config, and the prompt builders for `ChatModel` and `FeedbackModel`. | [README.md](app/models/README.md) |
| `services` | Runtime logic: chat and feedback generation, game mechanics, and session management. | [README.md](app/services/README.md) |

<div style="margin-top: 2.2em;"></div>

## 🛠️ Technical Requirements
The code was developed and run on `Python 3.12.3` on a macOS (`15.3.1`), but is currently served on a Linux server.

The project also requires:
| Tool     | Installation                                                                 |
|----------|--------------------------------------------------------------------------------------|
| [make](https://www.gnu.org/software/make/manual/make.html) | Installed via [Homebrew](https://formulae.brew.sh/formula/make)                  |
| [uv](https://docs.astral.sh/uv/)                         | Installed through this project's `makefile` (see [Usage](#Setup))                 |
        
## Project Setup
After having installed [make](https://www.gnu.org/software/make/manual/make.html), get started by:
```
make add-uv
make install
```
This installs `uv` and the project files onto your computer (omit first step if you have `uv` already)

## LLM Hosting Setup
Configuration is done via env files. My suggestion is to split into `.env.local` (dev) and `.env.prod` (production). See my configutations below

### Development 
For `env.local`, I would run Ollama locally on my Macbook and point to it like this:

```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
AVAILABLE_MODELS=llama3.2:3b,smollm2:360m
DEFAULT_MODEL=llama3.2:3b
```

> Ollama supports multiple models, and the user can switch between them at runtime. vLLM is bound to a single model. Make sure each model in `AVAILABLE_MODELS` has been pulled with `ollama pull <model>` before starting.

## Production
For `.env.prod`, I'm running vLLM served on a Nvidia DGX (using this [guide]())

```ini
LLM_PROVIDER=vllm
VLLM_BASE_URL=https://your-server.dk/v1
AVAILABLE_MODELS=google/gemma-4-26B-A4B-it
DEFAULT_MODEL=google/gemma-4-26B-A4B-it
```

> The model set as `DEFAULT_MODEL` must already be downloaded and running on the configured Ollama or vLLM instance.

### Anthropic Fallback (Optional)

The backend can fail over to Anthropic when the primary provider (Ollama or vLLM) becomes unreachable. The `health_monitor` service polls the primary on a fixed interval; on failure, in-flight chats are terminated and new chats are bound to Anthropic until the primary recovers. Add the following to your env file:

```ini
ANTHROPIC_API_KEY=sk-ant-XXXXXXX
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
ANTHROPIC_MODEL=claude-sonnet-4-6
CLAUDE_FALLBACK_ENABLED=true
PRIMARY_RECHECK_INTERVAL_S=10
```
> You naturally need to insert your own API key here :)

## 🚀 Run the Server
Once `.env.local` and `.env.prod` are in place:

```bash
make dev   # runs locally with .env.local
make prod  # runs locally with .env.prod
```

> Both commands run a local API that is not exposed to the internet. This is intentional: the frontend and backend share a server, and external traffic is handled at the infrastructure layer. The only difference between `dev` and `prod` is whether the inference server FastAPI talks to is local (Ollama) or remote (vLLM on DGX).