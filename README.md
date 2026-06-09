# Backend

FastAPI backend for the [InteractLLM frontend](https://github.com/INTERACT-LLM/frontend). 

Talks to LLMs through the OpenAI-compatible API, with vLLM, Ollama, and Anthropic as supported providers (see configuration below).

## 🌟 Overview
`app/main.py` is where the API logic is registered. The table below gives an overview of the `app` folder; deeper write-ups for individual subfolders live in their own `README.md`, linked in the "More Info" column.
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
For the LLM hosting setup, please refer to [docs/hosting_setup.md](/docs/hosting_setup.md).


## 🚀 Run the Server
Once you have followed the [Project setup](#project-setup) *and* the [LLM Hosting setup](docs/hosting_setup.md), with your `.env.local` and `.env.prod` in place, you can run:

```bash
make dev   # runs locally with .env.local
make prod  # runs locally with .env.prod
```

> Both commands run a local API that is not exposed to the internet. This is intentional: the frontend and backend share a server, and external traffic is handled at the infrastructure layer. The only difference between `dev` and `prod` is whether the inference server FastAPI talks to is local (Ollama) or remote (vLLM on DGX).