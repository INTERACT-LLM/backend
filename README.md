# Backend

FastAPI backend for the [InteractLLM frontend](https://github.com/INTERACT-LLM/frontend). 

LLM logic and inference for chat LLM and feedback LLMs (immediate and general feedback). Chat LLM has a bunch of lesson templates and prompt templates (see overview below). LLM inference is setup to run via OpenAI-compatiable APIs for vLLM, Ollama and Anthropic (see [LLM Hosting Setup](#llm-hosting-setup)).

## 🌟 Overview
`app/main.py` is where the API logic is. The table below gives an overview of the `app` folder; deeper write-ups for individual subfolders live in their own `README.md`, linked in the "More Info" column.
| 📁 Folder | Description | More Info |
| --- | --- | --- |
| `api` | Request entry and exit points for the backend. | |
| `data` | Lesson definitions and prompt templates. | |
| `models` | Data shapes: chat and feedback payloads, lesson and session config, and the prompt builders for `ChatModel` and `FeedbackModel`. | [README.md](app/models/README.md) |
| `services` | Runtime logic: chat and feedback generation, game mechanics, and session management. | [README.md](app/services/README.md) |

<div style="margin-top: 2.2em;"></div>

## 🛠️ Technical Requirements
The code was developed and run on `Python 3.12.3` on a macOS (`26.5.1`), but is currently served on a Linux server.

The project also requires:
| Tool     | Installation                                                                 |
|----------|--------------------------------------------------------------------------------------|
| [make](https://www.gnu.org/software/make/manual/make.html) | Installed via [Homebrew](https://formulae.brew.sh/formula/make)                  |
| [uv](https://docs.astral.sh/uv/)                         | Installed through this project's `makefile` (see [Usage](#Setup))                 |
        
## Project Setup
After having installed [make](https://www.gnu.org/software/make/manual/make.html), get started by:
```bash
make add-uv
make install
```
This installs `uv` and the project files onto your computer (omit first step if you have `uv` already)

## LLM Hosting Setup
To setup up LLM providers, please refer to [docs/hosting_setup.md](/docs/hosting_setup.md).


## 🚀 Run the Server
Once you have followed the [Project setup](#project-setup) *and* the [LLM Hosting setup](docs/hosting_setup.md), with your `.env.local` and `.env.prod` in place, you can run:

```bash
make dev   # runs locally with .env.local
make prod  # runs locally with .env.prod
```

> Both commands run a local API that is not exposed to the internet. This is intentional: the frontend and backend share a server, and external traffic is handled at the infrastructure layer. The only difference between `make dev` and `make prod` is whether you are running with .env.local or .env.prod. Local dev also has it setup so that the API updates when you make file changes (useful for testing).

### NB. Saving data!
> I've added this to the README temporarily, as per 11th of October 2026. The data logging was somewhat rushed and needs some more thought. Should be somewhat stable though!

**What**: Every chat is saved as a JSON file while it runs, together with a feedback file next to it.

**Where:** Folder is decided in `backend/app/services/store_interactions/set_storage.py`, in this order:

1. `set_chats_dir("some/path")` in Python (only affects that Python script, e.g. a test or analysis script)
2. `CHATS_DIR=some/path` in the env file (`.env.local` / `.env.prod`)
3. the default, `storage/chats` (next to `backend/`, not inside it)

Relative paths always start at the project root.

**Layout:**

```
storage/chats/
└── 2026-10-11/                              # day the chat started
    └── mina_3f2a9c1e/                       # username + first 8 chars of browser id
        ├── chat-<id>.json                   # messages, config, end reason, tabu events
        └── chat-<id>.feedback.json          # immediate feedback per message + general feedback
```

**Some documented fields for analysis:**
- `n_user_turns`: learner messages in the chat. `0` means the learner opened the chat but never wrote anything (e.g. a page refresh).
- `ended_reason`: `user_ended`, `restarted`, `provider_terminated`, `left_page`, or `null` (unknown).
- In the feedback file, `kind` is `immediate` or `general`, and `status` is `success` or `error` (with `error` and `raw_output` explaining failures in JSON formatting).

**Some good practice**
- Run the backend with **one worker only** (the default). Saving uses in-process locks, so several workers could overwrite each other's data. (NB: consider whether this should be changed at some point)
- **Back up `storage/` after every session**, e.g. to a university drive. It is the only copy.
- Don't point test/simulation at the real chats folder. Use a separate `CHATS_DIR` (see `.env.rehearsal`).