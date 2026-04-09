FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

WORKDIR /app

# Copy configuration files
COPY pyproject.toml uv.lock ./

# UV_COMPILE_BYTECODE for generating .pyc files -> faster application startup.
# UV_LINK_MODE=copy to silence warnings about not being able to use hard links
# since the cache and sync target are on separate file systems.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \ 
    uv sync --frozen --no-dev

# Copy source code
COPY src /app/src

# Final stage
FROM python:3.12.8-slim AS final

# Expose the port the application will run on
EXPOSE 8585

# PYTHONUNBUFFERED=1 to disable output buffering
ENV PYTHONUNBUFFERED=1
ARG VERSION=0.1.0
ENV APP_VERSION=$VERSION

# Set the working directory
WORKDIR /app

# Copy virtual environment from the base stage
COPY --from=base /app /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the Application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8585", "--workers", "4"]