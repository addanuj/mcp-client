# MCP Client Deployment Guide

## Quick Start

### Option 1: Docker Run (Recommended for Production)

```bash
# Create volume for config persistence
docker volume create mcp-client-data

# Run container
docker run -d \
  --name mcp-client \
  -p 8000:8000 \
  -v mcp-client-data:/root/.mcp-client \
  ghcr.io/addanuj/mcp-client:latest
```

### Option 2: Docker Compose

```bash
# Clone or create docker-compose.yml
docker compose up -d
```

### Option 3: Docker Run with Host Mount

```bash
# Create local config directory
mkdir -p ~/mcp-client-data

# Run container
docker run -d \
  --name mcp-client \
  -p 8000:8000 \
  -v ~/mcp-client-data:/root/.mcp-client \
  ghcr.io/addanuj/mcp-client:latest
```

## Important: Config Persistence

⚠️ **Always use a volume mount** (`-v`) to persist configuration:
- Model settings (API keys)
- MCP server connections
- Chat history
- User preferences

Without a volume, config is lost when container is removed.

## Access

- **Web UI**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

## Configuration

After starting the container:

1. Open http://localhost:8000 in your browser
2. Go to Settings (⚙️ icon)
3. Configure:
   - **Models**: Add OpenRouter/OpenAI API key
   - **MCP Servers**: Add QRadar MCP Server connection
   - **QRadar Connections**: Add QRadar instances

## Example: Full Setup

```bash
# 1. Create volume
docker volume create mcp-client-data

# 2. Run MCP Client
docker run -d \
  --name mcp-client \
  -p 8000:8000 \
  -v mcp-client-data:/root/.mcp-client \
  ghcr.io/addanuj/mcp-client:latest

# 3. Verify
curl http://localhost:8000/api/health

# 4. Open browser
open http://localhost:8000
```

## Backup Configuration

```bash
# Backup config
docker cp mcp-client:/root/.mcp-client/config.json ./backup-config.json

# Restore config
docker cp ./backup-config.json mcp-client:/root/.mcp-client/config.json
```

## Troubleshooting

### Config Not Persisting
**Problem**: Configuration lost after container restart

**Solution**: Ensure you're using a volume mount
```bash
docker run -d -v mcp-client-data:/root/.mcp-client ...
```

### Port Already in Use
**Problem**: `Error: port 8000 already allocated`

**Solution**: Use different port
```bash
docker run -d -p 8080:8000 ...  # Access on port 8080
```
