# LLM Hosting
Configuration is done via env files. The sections below describe my setup, which splits into `.env.local` (dev) and `.env.prod` (production). See my configutations below. 

> The model set as `DEFAULT_MODEL` must already be downloaded and running on the configured Ollama or vLLM instance.

## 👩🏻‍💻 Development 
For `env.local`, I would run Ollama locally on my Macbook and point to it like this:

```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
DEFAULT_MODEL=llama3.2:3b
```

### Install Ollama
Requires installing Ollama and making sure it is running: [https://ollama.com/download](https://ollama.com/download)

## 🏭 Production
For `.env.prod`, I'm running vLLM served on a Nvidia DGX:

```ini
LLM_PROVIDER=vllm
VLLM_BASE_URL=https://your-server.dk/v1
DEFAULT_MODEL=google/gemma-4-26B-A4B-it
```

### Installing vLLM 
I'm running on the Nvidia DGX, having followed their guide for downloading a specific docker image of vLLM (which works with gemma4): [https://build.nvidia.com/spark/vllm/instructions](https://build.nvidia.com/spark/vllm/instructions).

> You can also download vLLM in other ways and serve it, see their [docs](https://docs.vllm.ai/en/latest/serving/online_serving/) (untested).

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

## Ready to Run !
> [!TIP]
> Head over to the [Run the Server](../README.md#-run-the-server) section to start the application.