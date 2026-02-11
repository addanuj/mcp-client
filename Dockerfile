# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

LABEL org.opencontainers.image.source=https://github.com/anujshrivastava15/qradar-mcp-server
LABEL org.opencontainers.image.description="MCP Client - React + FastAPI Web UI for MCP Servers"

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python Backend + Frontend Static Files
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies + Docker CLI (static binary for MCP stdio transport)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.5.1.tgz | tar xz --strip-components=1 -C /usr/local/bin docker/docker \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Create log directory
RUN mkdir -p /var/log/mcp-client && chmod 777 /var/log/mcp-client

# Create config directory
RUN mkdir -p /root/.mcp-client

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV CONFIG_DIR=/root/.mcp-client

# Declare volume for config persistence
VOLUME ["/root/.mcp-client"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
