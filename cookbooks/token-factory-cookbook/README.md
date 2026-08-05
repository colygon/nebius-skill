Token Factory is Nebius's OpenAI-compatible LLM inference API: point the standard `openai` Python client (or any OpenAI-compatible tool) at `https://api.tokenfactory.nebius.com/v1` with a Nebius API key and you get chat completions, function calling, and tool-use loops against models like `nvidia/nemotron-3-super-120b-a12b`.

This cookbook covers the recipes we ship with the `/tokenfactory` skill: a minimal quickstart, a full function-calling loop, routing through LiteLLM for multi-provider setups, wiring a Token Factory model to live MCP (Model Context Protocol) tools via LangGraph, and deploying a Token Factory-backed agent as a public endpoint on Nebius Serverless. Every snippet below is runnable as-is once you export `NEBIUS_API_KEY`.

## How to make your first Token Factory call with the OpenAI SDK

You have a Nebius API key and want the fastest path to a working chat completion against a Token Factory model, using tooling you already know.

**Prerequisites**
- Python 3.9+
- pip install openai
- A Nebius API key exported as NEBIUS_API_KEY
- Optional: NEBIUS_BASE_URL if your dashboard shows a region-specific endpoint

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a concise data analyst."},
        {"role": "user", "content": "In one sentence, what is a yield excursion?"},
    ],
    temperature=0.2,
)
print(resp.choices[0].message.content)
```

Token Factory speaks the OpenAI Chat Completions protocol, so you use the real `openai` Python package unmodified: only `base_url` and `api_key` change. `base_url` defaults to `https://api.tokenfactory.nebius.com/v1`, but confirm the exact value in your Nebius dashboard since some regions (see the OpenClaw deployment recipe below) use a region-suffixed URL like `https://api.tokenfactory.us-central1.nebius.com/v1`. `api_key` comes straight from `os.environ["NEBIUS_API_KEY"]`, no fallback, so the script fails fast if the key isn't set. `MODEL` is the Token Factory model ID; `nvidia/nemotron-3-super-120b-a12b` is the one used throughout Nebius's own examples.

**Expected output**

```
A single sentence definition of a yield excursion, printed to stdout, e.g. something like: "A yield excursion is a temporary, sharp deviation of a bond's yield from its expected trading range." (exact wording varies by run since temperature is 0.2, not 0).
```

**Gotchas**
- If NEBIUS_API_KEY isn't exported, Python raises a KeyError before any network call is made, there's no silent fallback.
- Double-check the /v1 suffix on NEBIUS_BASE_URL; omitting it breaks every OpenAI-SDK call.
- Lower temperature (0.2 here) trades response variety for consistency, raise it for more creative outputs.

## How to build a function-calling agent loop with Token Factory

You want a Token Factory model to decide when to call your tools (APIs, databases, or MCP tools), execute them, and keep going until the question is answered.

**Prerequisites**
- pip install openai
- NEBIUS_API_KEY and NEBIUS_BASE_URL exported
- Real tool implementations to swap in for the stubs (API calls, DB queries, or an MCP session.call_tool)

```python
import os, json
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
)
MODEL = "nvidia/nemotron-3-super-120b-a12b"

TOOLS = [
    {"type": "function", "function": {
        "name": "search_products",
        "description": "Search the product catalog and return matching products.",
        "parameters": {"type": "object",
            "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_top_categories",
        "description": "Return a customer's top product categories by total spend.",
        "parameters": {"type": "object",
            "properties": {"customer_id": {"type": "integer"}},
            "required": ["customer_id"]}}},
]


def call_tool(name, args):
    """STUB — replace with real implementations (API, DB, or MCP session.call_tool)."""
    if name == "search_products":
        return {"products": [{"name": "Linen Jumpsuit", "category": "Jumpsuits & Rompers"}]}
    if name == "get_top_categories":
        return {"categories": [{"category": "Jumpsuits & Rompers", "spend": 412.0},
                               {"category": "Outerwear", "spend": 267.5}]}
    return {"error": f"unknown tool {name}"}


def run(question):
    messages = [
        {"role": "system", "content": "You answer questions using the provided tools. "
                                      "Stop when the question is answered."},
        {"role": "user", "content": question},
    ]
    for _ in range(12):  # safety bound on tool-calling turns
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto")
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
                result = call_tool(tc.function.name, args)
            except Exception as e:  # return errors to the model so it can recover
                result = {"error": str(e)}
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(result)})
    return "(stopped: too many tool-calling turns)"


if __name__ == "__main__":
    print(run("What are the top categories by spend for customer 42?"))
```

`TOOLS` declares two OpenAI-style function schemas with `name`, `description`, and JSON-Schema `parameters`. `run()` sends the conversation with `tools=TOOLS` and `tool_choice="auto"`, letting the model decide whether to call a tool or answer directly. As long as `msg.tool_calls` is non-empty, the loop appends the assistant's tool-call message, executes each call through `call_tool`, and appends a `role: "tool"` message keyed by `tool_call_id` with the JSON result. The loop caps at 12 iterations so a model stuck in a call-call-call pattern can't run forever. `call_tool` here is a labeled STUB, in production this is where you plug in a real product-search API, a database query, or an MCP `session.call_tool` dispatch.

**Expected output**

```
Prints a natural-language answer synthesized from the stub data, along the lines of: "Customer 42's top categories by spend are Jumpsuits & Rompers ($412.00) and Outerwear ($267.50)."
```

**Gotchas**
- Exceptions from call_tool are caught and sent back to the model as {"error":...} instead of crashing the loop, this lets the model retry with different arguments or explain the failure.
- The 12-turn cap is a safety bound, not a tuning knob to increase casually; a well-scoped tool set should resolve most questions in 1-3 turns.
- Every tool message must carry the matching tool_call_id from the assistant's tool_calls entry or the next request will be rejected.

## How to call Token Factory through LiteLLM

You're running a multi-provider agent or eval harness on LiteLLM and want to add Token Factory models without a separate client.

**Prerequisites**
- pip install litellm
- NEBIUS_API_KEY exported

```python
import litellm

resp = litellm.completion(
    model="nebius/nvidia/nemotron-3-super-120b-a12b",   # LiteLLM format: nebius/<model-id>
    messages=[{"role": "user", "content": "List three anomaly-detection ideas for e-commerce orders."}],
    temperature=0.3,
)
print(resp.choices[0].message.content)
```

LiteLLM routes by model-string prefix. Prefixing the Token Factory model ID with `nebius/` (giving `nebius/nvidia/nemotron-3-super-120b-a12b`) tells LiteLLM which provider adapter to use; it reads `NEBIUS_API_KEY` from the environment the same way the OpenAI SDK does. This is the pattern to use when your agent framework or eval suite is already built on `litellm.completion` and you want to add Token Factory as one of several backends without branching your call sites.

**Expected output**

```
A numbered or bulleted list of three anomaly-detection ideas for e-commerce orders, printed to stdout.
```

**Gotchas**
- Forgetting the nebius/ prefix causes LiteLLM to route to the wrong provider or fail to resolve the model.
- LiteLLM still needs NEBIUS_API_KEY in the environment, it does not read NEBIUS_BASE_URL by default in this snippet, so use the plain OpenAI SDK example instead if you need a custom base URL.

## How to connect a Token Factory model to live MCP tools with LangGraph

You want an agent that discovers and calls tools from a running MCP (Model Context Protocol) server at runtime, instead of hand-writing a tool-dispatch loop.

**Prerequisites**
- pip install langgraph langchain-openai langchain-mcp-adapters
- NEBIUS_API_KEY and NEBIUS_BASE_URL exported
- MCP_SERVER_URL and MCP_API_KEY exported, pointing at a running MCP server
- Know your MCP server's transport (sse, streamable_http, or stdio)

```python
import os, asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
    model="nvidia/nemotron-3-super-120b-a12b",
    temperature=0.2,
)


async def main():
    client = MultiServerMCPClient({
        "tools": {
            "url": os.environ["MCP_SERVER_URL"],
            "transport": "sse",   # match your server's transport (sse / streamable_http / stdio)
            "headers": {"Authorization": f"Bearer {os.environ['MCP_API_KEY']}"},
        }
    })
    tools = await client.get_tools()            # real tools, discovered live
    agent = create_react_agent(llm, tools)

    result = await agent.ainvoke({"messages": [
        {"role": "system", "content": "Answer using the available tools; don't guess at "
                                      "data you could fetch."},
        {"role": "user", "content": "What tools do you have, and what can you do with them?"},
    ]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
```

`ChatOpenAI` from `langchain-openai` is pointed at Token Factory the same way the raw OpenAI client is: `base_url` plus `api_key`. `MultiServerMCPClient` from `langchain-mcp-adapters` connects to one or more MCP servers, here a single server named `"tools"`, and `await client.get_tools()` fetches the live tool list, converted into LangChain tool objects. `create_react_agent(llm, tools)` builds a LangGraph prebuilt ReAct agent that owns the tool-dispatch loop for you, so you don't hand-write the `tool_calls` handling from the function-calling recipe above. `agent.ainvoke` runs the conversation and returns the final assistant message.

**Expected output**

```
Prints the agent's description of the tools it discovered from your MCP server and what it can do with them — content depends entirely on what your MCP server exposes.
```

**Gotchas**
- transport must match your MCP server exactly, sse, streamable_http, and stdio are not interchangeable, and a mismatch fails the connection before any tool call happens.
- Tools are discovered live at startup via get_tools(); if the MCP server is down or the URL is wrong, this call fails before the agent ever talks to Token Factory.
- The Authorization header uses Bearer plus MCP_API_KEY, this is separate from your NEBIUS_API_KEY and authenticates against the MCP server, not Token Factory.

## How to deploy a Token Factory-backed agent on Nebius Serverless

You've built an agent that calls Token Factory and want it running as a public HTTP endpoint, without building a custom Docker image.

**Prerequisites**
- Nebius CLI installed and authenticated (nebius profile create)
- jq and openssl installed
- A Token Factory API key from https://tokenfactory.nebius.com
- An SSH key pair (id_ed25519 preferred)

```bash
# 1. Choose your model
MODEL="zai-org/GLM-5"
# Other options: deepseek-ai/DeepSeek-R1-0528, MiniMaxAI/MiniMax-M2.5, zai-org/GLM-4.5

# 2. Get your Token Factory API key (set manually from https://tokenfactory.nebius.com)
TF_KEY="v1.xxx..."

# 3. Set region and Token Factory URL
REGION="eu-north1"    # or eu-west1, us-central1
PLATFORM="cpu-e2"     # eu-west1 uses cpu-d3
if [[ "$REGION" == "us-central1" ]]; then
  TOKEN_FACTORY_URL="https://api.tokenfactory.us-central1.nebius.com/v1"
else
  TOKEN_FACTORY_URL="https://api.tokenfactory.nebius.com/v1"
fi

# 4. Generate a gateway password
PASSWORD=$(openssl rand -hex 16)
echo "Save this password: $PASSWORD"

# 5. Deploy
nebius ai endpoint create \
  --name openclaw-agent \
  --image ghcr.io/opencolin/openclaw-serverless:latest \
  --platform $PLATFORM \
  --preset 2vcpu-8gb \
  --container-port 8080 \
  --container-port 18789 \
  --disk-size 250Gi \
  --env "TOKEN_FACTORY_API_KEY=${TF_KEY}" \
  --env "TOKEN_FACTORY_URL=${TOKEN_FACTORY_URL}" \
  --env "INFERENCE_MODEL=${MODEL}" \
  --env "OPENCLAW_WEB_PASSWORD=${PASSWORD}" \
  --public \
  --ssh-key "$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || echo '')" \
  --format json

# 6. Wait for RUNNING
ENDPOINT_ID=$(nebius ai endpoint get-by-name openclaw-agent --format json | jq -r '.metadata.id')
while true; do
  STATE=$(nebius ai endpoint get $ENDPOINT_ID --format json | jq -r '.status.state')
  echo "Status: $STATE"
  [ "$STATE" = "RUNNING" ] && break
  sleep 10
done

# 7. Get the public IP
IP=$(nebius ai endpoint get $ENDPOINT_ID --format json \
  | jq -r '.status.instances[0].public_ip' | cut -d/ -f1)
echo "Endpoint IP: $IP"

# 8. Verify
curl http://$IP:8080
```

This deploys the public `ghcr.io/opencolin/openclaw-serverless:latest` image as a Nebius AI Serverless endpoint, wired to Token Factory purely through environment variables: `TOKEN_FACTORY_API_KEY` and `TOKEN_FACTORY_URL` tell the container which Token Factory account and region endpoint to call, and `INFERENCE_MODEL` picks the model it runs (`zai-org/GLM-5`, `deepseek-ai/DeepSeek-R1-0528`, `MiniMaxAI/MiniMax-M2.5`, or `zai-org/GLM-4.5`). `TOKEN_FACTORY_URL` branches on region: `us-central1` uses `https://api.tokenfactory.us-central1.nebius.com/v1`, every other region uses `https://api.tokenfactory.nebius.com/v1`. `--platform` also depends on region, `cpu-e2` for `eu-north1`/`us-central1`, `cpu-d3` for `eu-west1`. The script polls `nebius ai endpoint get` until `status.state` reports `RUNNING`, then strips the `/32` CIDR suffix from the reported public IP before curling the container's health check on port 8080.

**Expected output**

```
The final curl prints a JSON health response: {"status":"healthy","service":"openclaw-serverless","model":"zai-org/GLM-5",...}
```

**Gotchas**
- PLATFORM must match REGION (cpu-e2 for eu-north1/us-central1, cpu-d3 for eu-west1), deploying with the wrong platform for a region fails at creation.
- TOKEN_FACTORY_URL must match the region branch exactly; using the default URL in us-central1 points the container at the wrong backend.
- The public IP from nebius ai endpoint get includes a /32 CIDR suffix, strip it with cut -d/ -f1 before using it in curl or SSH commands.
- To reach the agent's dashboard or TUI (port 18789) you need an SSH tunnel first, browsers block device pairing without HTTPS or localhost, so connect via ssh -f -N -L 28789:$IP:18789 nebius@$IP and use http://localhost:28789, never the direct IP.

## FAQ

### What base URL and API key does Token Factory use with the OpenAI SDK?

Set base_url to https://api.tokenfactory.nebius.com/v1 (confirm the exact value in your Nebius dashboard, since some regions like us-central1 use https://api.tokenfactory.us-central1.nebius.com/v1) and api_key to your NEBIUS_API_KEY.

### Which Token Factory model should I start with?

The examples in this cookbook use nvidia/nemotron-3-super-120b-a12b for chat completions and function calling. For the OpenClaw serverless deployment, zai-org/GLM-5, deepseek-ai/DeepSeek-R1-0528, MiniMaxAI/MiniMax-M2.5, and zai-org/GLM-4.5 are also supported via the INFERENCE_MODEL environment variable.

### Can I use Token Factory with frameworks other than the raw OpenAI SDK?

Yes. LiteLLM works with the model string nebius/<model-id> (e.g. nebius/nvidia/nemotron-3-super-120b-a12b), and LangChain/LangGraph work by pointing ChatOpenAI's base_url and api_key at Token Factory just like the OpenAI client.

### How do I connect a Token Factory model to external tools?

For hand-rolled control, use the OpenAI SDK's tools/tool_choice parameters in a loop that dispatches tool_calls and feeds results back as role: "tool" messages. For live tool discovery from an MCP server, use langchain-mcp-adapters' MultiServerMCPClient with LangGraph's create_react_agent, which handles the dispatch loop for you.

### How do I run a Token Factory agent as a public endpoint instead of a local script?

Deploy the ghcr.io/opencolin/openclaw-serverless:latest image with nebius ai endpoint create, passing TOKEN_FACTORY_API_KEY, TOKEN_FACTORY_URL, and INFERENCE_MODEL as environment variables. Poll nebius ai endpoint get until status.state is RUNNING, then reach the container on the reported public IP.

## Key takeaways

- Token Factory is OpenAI-compatible: only base_url and api_key differ from a normal OpenAI SDK call.
- The function-calling loop pattern (tools + tool_choice="auto" + tool_call_id-keyed responses) is the core building block for any Token Factory agent, and it caps turns to avoid runaway loops.
- LiteLLM routes to Token Factory via the nebius/<model-id> prefix, useful for multi-provider agents and evals.
- LangGraph's create_react_agent plus langchain-mcp-adapters lets a Token Factory model call live MCP tools without a hand-written dispatch loop.
- Deploying a Token Factory agent on Nebius Serverless is env-var driven (TOKEN_FACTORY_API_KEY, TOKEN_FACTORY_URL, INFERENCE_MODEL) and region determines both the platform (cpu-e2 vs cpu-d3) and the Token Factory URL.