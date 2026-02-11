"""Chat router - streaming chat with PydanticAI agent."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator
import json
import logging

from app.models.schemas import ChatStreamRequest
from app.pydantic_agent import create_agent, run_agent_sync
from app import config_store

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_agent_config(mcp_servers):
    """Get LLM config and inject QRadar credentials into MCP servers."""
    models = config_store.get_llm_models()
    if not models:
        return None, None, None, "No LLM models configured"

    llm_config = next((m for m in models if m.get("is_default")), models[0])
    provider = llm_config.get("provider", "openrouter")
    api_key = llm_config.get("api_key", "")
    model_id = llm_config.get("name", llm_config.get("model_id"))

    if provider == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
    elif provider == "openai":
        base_url = "https://api.openai.com/v1"
    else:
        base_url = llm_config.get("base_url", "https://openrouter.ai/api/v1")

    # Inject QRadar credentials
    for server in mcp_servers:
        if server.get("qradarConnectionId"):
            qradar_conn = config_store.get_qradar_connection(server["qradarConnectionId"])
            if qradar_conn:
                env_vars = server.get("env", {})
                if isinstance(env_vars, str):
                    env_vars = {}
                env_vars["QRADAR_HOST"] = qradar_conn.get("url", "")
                env_vars["QRADAR_API_TOKEN"] = qradar_conn.get("token", "")
                server["env"] = env_vars

    return model_id, base_url, api_key, None


async def stream_chat(request: ChatStreamRequest) -> AsyncGenerator[str, None]:
    """Stream chat responses using PydanticAI agent."""
    try:
        mcp_servers = config_store.get_mcp_servers()
        if not mcp_servers:
            yield f"data: {json.dumps({'type': 'error', 'content': 'No MCP servers configured'})}\n\n"
            return

        model_id, base_url, api_key, error = _get_agent_config(mcp_servers)
        if error:
            yield f"data: {json.dumps({'type': 'error', 'content': error})}\n\n"
            return

        async for event in create_agent(
            model=model_id, base_url=base_url, api_key=api_key,
            mcp_servers=mcp_servers, message=request.message,
        ):
            yield f"data: {json.dumps(event)}\n\n"
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatStreamRequest):
    """Stream chat responses via SSE."""
    return StreamingResponse(
        stream_chat(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/ask")
async def chat_ask(request: ChatStreamRequest):
    """Non-streaming chat endpoint. Returns full response as JSON."""
    try:
        mcp_servers = config_store.get_mcp_servers()
        if not mcp_servers:
            raise HTTPException(status_code=400, detail="No MCP servers configured")

        model_id, base_url, api_key, error = _get_agent_config(mcp_servers)
        if error:
            raise HTTPException(status_code=400, detail=error)

        result = await run_agent_sync(
            model=model_id, base_url=base_url, api_key=api_key,
            mcp_servers=mcp_servers, message=request.message,
        )
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
