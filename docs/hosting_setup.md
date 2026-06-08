# LLM Hosting
Configuration is done via env files. My suggestion is to split into `.env.local` (dev) and `.env.prod` (production). See my configutations below:

## 👩🏻‍💻 Development 
For `env.local`, I would run Ollama locally on my Macbook and point to it like this:

```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
AVAILABLE_MODELS=llama3.2:3b,smollm2:360m
DEFAULT_MODEL=llama3.2:3b
```

> Ollama supports multiple models, and the user can switch between them at runtime. vLLM is bound to a single model. Make sure each model in `AVAILABLE_MODELS` has been pulled with `ollama pull <model>` before starting.

### Install Ollama
Naturally requires installing Ollama and making sure it is running when you need it: [https://ollama.com/download](https://ollama.com/download)

## 🏭 Production
For `.env.prod`, I'm running vLLM served on a Nvidia DGX:

```ini
LLM_PROVIDER=vllm
VLLM_BASE_URL=https://your-server.dk/v1
AVAILABLE_MODELS=google/gemma-4-26B-A4B-it
DEFAULT_MODEL=google/gemma-4-26B-A4B-it
```

> The model set as `DEFAULT_MODEL` must already be downloaded and running on the configured Ollama or vLLM instance.

### Installing vLLM 
I'm running on the Nvidia DGX, having followed their guide for downloading a specific docker image of vLLM (which works with gemma4): [https://build.nvidia.com/spark/vllm/instructions](https://build.nvidia.com/spark/vllm/instructions).

### Anthropic Fallback (Optional)

The backend can fail over to Anthropic when the primary provider (Ollama or vLLM) becomes unreachable. The `health_monitor` service polls the primary on a fixed interval; on failure, in-flight chats are terminated and new chats are bound to Anthropic until the primary recovers. Add the following to your env file:

```ini
ANTHROPIC_API_KEY=sk-ant-XXXXXXX
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
ANTHROPIC_MODEL=claude-sonnet-4-6
CLAUDE_FALLBACK_ENABLED=true
PRIMARY_RECHECK_INTERVAL_S=30
```
Note that
* You naturally need to insert your own API key !
*  `PRIMARY_RECHECK_INTERVAL_S` controls how often it polls the primary provider. Setting it higher will lead to users being on the Anthropic API for longer, whereas shorter intervals might make the backend switch back to the primary provider (if that is live)