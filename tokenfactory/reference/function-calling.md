# Function / Tool Calling

Nemotron on Token Factory supports OpenAI-style tool calling. The agent loop is:

1. Send `messages` + `tools` to the model.
2. Model returns `tool_calls` (name + JSON args).
3. **You execute the tool** — a local function, an API call, or an MCP server tool
   (for MCP dispatch, see `mcp-integration.md`).
4. Append the tool result as a `role: "tool"` message.
5. Loop until the model answers with no more tool calls.

## Declaring tools to the model

Describe each tool as an OpenAI function schema. Illustrative example:

```python
tools = [
    {"type": "function", "function": {
        "name": "search_products",
        "description": "Search the product catalog and return matching products.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_top_categories",
        "description": "Return a customer's top product categories by total spend.",
        "parameters": {"type": "object", "properties": {
            "customer_id": {"type": "integer"}}, "required": ["customer_id"]}}},
]
```

> If your tools live on an MCP server, don't hardcode schemas — list the server's tools at
> runtime and build this array from what it advertises (see `mcp-integration.md`).

## The loop (OpenAI SDK)

```python
from openai import OpenAI
import json, os

client = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])
MODEL = "nvidia/nemotron-3-super-120b-a12b"

def call_tool(name, args):
    # Dispatch to your implementation: local function, API, or MCP session.call_tool.
    return my_tools[name](**args)   # returns a JSON-serializable result

messages = [
    {"role": "system", "content": "You answer questions using the provided tools. "
                                   "Stop once the question is answered."},
    {"role": "user", "content": "What are the top 6 product categories by spend for customer 42?"},
]

for _ in range(12):  # safety bound on tool-calling turns
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools, tool_choice="auto")
    msg = resp.choices[0].message
    messages.append(msg)

    if not msg.tool_calls:
        print(msg.content)   # final answer
        break

    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments or "{}")
        result = call_tool(tc.function.name, args)
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result),
        })
```

Runnable version (with stub tools and error handling): `examples/function_calling.py`.

## Tips

- **Guide the model** in the system prompt: say which tool to prefer for which job, page
  large results, and stop once the question is answered.
- **Keep tool results compact** — pass summaries or references, not thousands of raw rows,
  to stay within context and keep the model focused.
- **Handle malformed args**: models occasionally emit slightly invalid JSON — wrap `json.loads`
  in a try/except and, on failure, return an error message as the tool result so the model retries.
- **`tool_choice`**: use `"auto"` normally; force a specific tool with
  `{"type": "function", "function": {"name": "search_products"}}` when you want to seed the loop.
- **Bound the loop** (`for _ in range(12)` above) so a confused model can't spin forever.
