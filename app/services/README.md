The `services` folder contains:

## LLMs
The LLM generation logic for the chat and feedback model

| Name | Purpose |
| --- | --- |
| `chat` | Handles chat turns: builds the system prompt, streams the assistant's response, persists history, and terminates the chat on provider failure (chat model). |
| `feedback` | Generates immediate and general feedback on student messages by calling the LLM with structured JSON prompts. (feedback model) |

## Utils Files
Load lessons, configure how models should be loaded & a small game_utils (for drawing a random word)

| Name | Purpose |
| --- | --- |
| `load_lessons` | Loads lesson configuration from TOML files on disk. |
| `model_config` | Resolves the OpenAI-compatible client and model name for the currently active provider. |
| `game_utils` | Helper file for the 20Q game. |

## Storing and Status
Hold and check LLM provider state, stroe chat and session (in-memory)
| Name | Purpose |
| --- | --- |
| `provider_state` | Holds the currently active LLM provider and exposes safe failover/failback transitions. |
| `health_monitor` | Background task that pings the primary provider on a schedule and updates `provider_state`. |
| `store_chat` | Persists and retrieves chat state (messages, snapshotted config, provider, model). |
| `store_session` | In-memory store for session config (user identity and profile). To be replaced with persistent storage at some point. |