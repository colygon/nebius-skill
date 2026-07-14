# MCP Tools + Token Factory — End to End

The core agent architecture: your model on Token Factory does the reasoning and decides
which tools to call; the tools — often exposed by an **MCP server** (a data platform,
search service, browser, or your own) — do the real work.

```
                 tool calls                         MCP
  ┌─────────┐  ───────────────►  ┌───────────────┐ ─────► ┌──────────────────┐
  │  Your   │                    │  Your agent   │        │   MCP server(s)   │──► data, search,
  │  model  │  ◄───────────────  │  (glue code)  │ ◄───── │  (any provider)   │    APIs, ...
  │ (Nebius)│   tool results     └───────────────┘  data  └──────────────────┘
  └─────────┘
```

- **Token Factory** runs the *reasoning* model that decides what to do.
- **The MCP server** advertises tools and executes them.
- **Your glue code** relays tool calls from the model to the server and results back.

## Two ways to connect the model to an MCP server

### A) Manual dispatch (most control)

Use the function-calling loop in `function-calling.md`. You keep an MCP client to the
server and, when the model emits a tool call, you invoke the matching MCP tool.

Minimal MCP client (Python `mcp` package):

```python
from contextlib import asynccontextmanager
from mcp import ClientSession
from mcp.client.sse import sse_client   # or stdio_client / streamablehttp_client, per the server's transport
import os

# Endpoint + auth come from whoever runs the MCP server.
MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]
MCP_API_KEY = os.environ["MCP_API_KEY"]

@asynccontextmanager
async def mcp_session():
    async with sse_client(MCP_SERVER_URL, headers={"Authorization": f"Bearer {MCP_API_KEY}"}) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            yield session

async def main():
    # The session dies when its context exits — keep the whole model loop inside it.
    async with mcp_session() as session:
        tools = await session.list_tools()          # discover real tool names/params
        ...                                          # run your model loop here:
        # result = await session.call_tool(name, arguments)
```

### B) Framework MCP adapter (least glue)

Frameworks like LangGraph / LangChain can load MCP tools directly and bind them to a
`ChatOpenAI` pointed at Token Factory — the framework handles the dispatch loop for you.
See `examples/langgraph_mcp_agent.py`.

## Discover tools at runtime — don't hardcode

An MCP server advertises its own tools. Always `list_tools()` first and build your
OpenAI `tools` array from that, so names/params match the live server.

## Environment summary

```bash
# Inference (Nebius Token Factory)
export NEBIUS_API_KEY="..."
export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
# Tools (MCP) — from whoever runs the server
export MCP_SERVER_URL="your-mcp-endpoint"
export MCP_API_KEY="..."
```
