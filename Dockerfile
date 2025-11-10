# JVLink MCP Server - Docker Image
# Multi-stage build for optimized image size

FROM python:3.11-slim AS builder

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -r pyproject.toml


# Final stage - minimal runtime image
FROM python:3.11-slim

# Install required system packages for database drivers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser README.md ./

# Create directory for database files (if using SQLite/DuckDB)
RUN mkdir -p /data && chown appuser:appuser /data

# Switch to non-root user
USER appuser

# Environment variables (can be overridden)
ENV DB_TYPE=sqlite
ENV DB_PATH=/data/race.db
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port for SSE mode
EXPOSE 8000

# Default command: Run in stdio mode for local connections
# Override with docker-compose for SSE mode
CMD ["python", "-m", "jvlink_mcp_server.server"]
