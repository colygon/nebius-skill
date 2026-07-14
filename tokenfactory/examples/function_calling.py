"""Function-calling loop: a Token Factory model drives your tools.

This is the core agent pattern. The tools here are illustrative STUBS — swap in real
implementations: API calls, database queries, or MCP server tools (for MCP dispatch,
see reference/mcp-integration.md).

Setup:
    pip install openai
    export NEBIUS_API_KEY="your-key"
    export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
"""
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
