"""LangGraph agent: a Token Factory model + MCP server tools (adapter approach).

Frameworks can load MCP tools and run the tool-dispatch loop for you. Here LangGraph's
prebuilt ReAct agent uses a ChatOpenAI pointed at Token Factory, with an MCP server's
tools loaded via langchain-mcp-adapters. Works with any MCP server — point the env vars
at yours.

Setup:
    pip install langgraph langchain-openai langchain-mcp-adapters
    export NEBIUS_API_KEY="your-key"
    export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
    export MCP_SERVER_URL="your-mcp-endpoint"
    export MCP_API_KEY="your-mcp-key"
"""
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
