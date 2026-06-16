The `models` folder contains:

## Data
Passive Pydantic shapes for request/response payloads. No behaviour. Used for LLM logic e.g., [app/services/chat.py](/app/services/chat.py) and API requests e.g., [app/api/chat.py](/app/api/chat.py)

| Name | Purpose |
| --- | --- |
| `chat` | Schemas for chat messages, chat state, and chat-endpoint requests. |
| `feedback` | Schemas for feedback responses and feedback-endpoint requests. |

## Environments (env configs)
Configuration that defines the context a chat or feedback turn runs in: who the user is, what lesson they're doing.

| Name | Purpose |
| --- | --- |
| `lesson` | Lesson config (UI presentation, instructions per lesson type, feedback focus). |
| `session` | User session config (name, language, proficiency level). |

> NB. Environments is a made up name; no idea what the convention is!

## LLMs
Wrappers that define how a model should behave for a given task: build prompts, hold per-call parameters. They do not call the LLM. That lives in [app/services](/app/services/).

| Name | Purpose |
| --- | --- |
| `chat_model` | Build the system prompt and chat-call parameters from session and lesson config. |
| `feedback_model` | Building the immediate and general feedback prompts from session, lesson, and conversation. |