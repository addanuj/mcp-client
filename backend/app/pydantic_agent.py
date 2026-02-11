"""
PydanticAI-based MCP Agent with native MCP support.

Uses PydanticAI's built-in MCPServerSSE and MCPServerStdio for
connecting to MCP servers. Replaces 850-line LangGraph agent.
"""

import json
import logging
import os
from typing import AsyncGenerator

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio

logger = logging.getLogger(__name__)


def _build_toolsets(mcp_servers: list[dict]):
    """Build MCP server toolsets from config."""
    toolsets = []
    server_names = []
    stages = []

    for cfg in mcp_servers:
        name = cfg.get("name", "Unknown")
        transport = cfg.get("transport", "sse")
        server_url = cfg.get("serverUrl", "")

        try:
            if transport == "stdio":
                command = cfg.get("command", "docker")
                args = list(cfg.get("args", []))
                env_vars = cfg.get("env")
                if env_vars and isinstance(env_vars, dict) and env_vars:
                    env_merged = dict(os.environ)
                    env_merged.update(env_vars)
                    mcp_server = MCPServerStdio(command, args=args, env=env_merged, timeout=30)
                else:
                    mcp_server = MCPServerStdio(command, args=args, timeout=30)
                toolsets.append(mcp_server)
                server_names.append(name)
                stages.append({"type": "stage", "content": f"Connecting to {name} (stdio)..."})
            else:
                if not server_url:
                    stages.append({"type": "error", "content": f"No serverUrl for {name}, skipping"})
                    continue
                sse_url = f"{server_url.rstrip('/')}/sse"
                toolsets.append(MCPServerSSE(sse_url, timeout=30))
                server_names.append(name)
                stages.append({"type": "stage", "content": f"Connecting to {name} (sse)..."})
        except Exception as e:
            logger.error(f"Failed to configure {name}: {e}")
            stages.append({"type": "error", "content": f"Failed to configure {name}: {str(e)}"})

    return toolsets, server_names, stages


async def create_agent(
    model: str,
    base_url: str,
    api_key: str,
    mcp_servers: list[dict],
    message: str,
) -> AsyncGenerator[dict, None]:
    """Create and run PydanticAI agent with native MCP support."""
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    llm = OpenAIModel(model, provider=provider)

    toolsets, server_names, stages = _build_toolsets(mcp_servers)

    for stage in stages:
        yield stage

    if not toolsets:
        yield {"type": "error", "content": "No MCP servers available"}
        return

    agent = Agent(
        model=llm,
        system_prompt=(
            "You are an AI assistant with access to IBM security tools via MCP servers.\n\n"
            "Available MCP Servers and their tools:\n"
            "- QRadar MCP Server: Query IBM QRadar SIEM - use tools like qradar_get, qradar_post, "
            "search_offenses, execute_aql, etc.\n"
            "- GCM MCP Server: Query IBM Guardium Cryptographic Manager - use tools like gcm_api, "
            "list_services, get_health, etc.\n\n"
            "When asked about versions:\n"
            "- QRadar version: use qradar_get with endpoint=\"/system/about\"\n"
            "- GCM version: use gcm_api with service=\"config\", endpoint=\"/version\"\n\n"
            "Always pick the correct server's tools based on the product being asked about.\n"
            "Return results clearly formatted."
        ),
        toolsets=toolsets,
    )

    yield {"type": "stage", "content": f"Connected to {len(toolsets)} MCP servers: {', '.join(server_names)}"}
    yield {"type": "stage", "content": "Running agent..."}

    try:
        result = await agent.run(message)
        logger.info(f"Agent completed, output: {result.output[:200]}")
        yield {"type": "message", "content": result.output}
        yield {"type": "done", "content": ""}
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        yield {"type": "error", "content": str(e)}


async def run_agent_sync(
    model: str,
    base_url: str,
    api_key: str,
    mcp_servers: list[dict],
    message: str,
) -> dict:
    """Non-streaming agent run. Returns final result directly."""
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    llm = OpenAIModel(model, provider=provider)

    toolsets, server_names, _ = _build_toolsets(mcp_servers)

    if not toolsets:
        return {"error": "No MCP servers available"}

    agent = Agent(
        model=llm,
        system_prompt=(
            "You are an AI assistant with access to IBM security tools via MCP servers.\n\n"
            "Available MCP Servers and their tools:\n"
            "- QRadar MCP Server: Query IBM QRadar SIEM - use tools like qradar_get, qradar_post, "
            "search_offenses, execute_aql, etc.\n"
            "- GCM MCP Server: Query IBM Guardium Cryptographic Manager - use tools like gcm_api, "
            "list_services, get_health, etc.\n\n"
            "When asked about versions:\n"
            "- QRadar version: use qradar_get with endpoint=\"/system/about\"\n"
            "- GCM version: use gcm_api with service=\"config\", endpoint=\"/version\"\n\n"
            "Always pick the correct server's tools based on the product being asked about.\n"
            "Return results clearly formatted."
        ),
        toolsets=toolsets,
    )

    logger.info(f"Running agent (sync) with {len(toolsets)} servers: {', '.join(server_names)}")
    result = await agent.run(message)
    logger.info(f"Agent completed, output: {result.output[:200]}")
    return {"content": result.output, "servers": server_names}
