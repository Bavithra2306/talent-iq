
# 1. Start with Python 3.13
FROM python:3.13-slim

# 2. Set the application working directory
WORKDIR /app

# 3. Configure Python and uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 4. Install uv from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 5. Copy dependency definitions first
COPY pyproject.toml uv.lock ./

# 6. Install locked dependencies without installing the project itself
RUN uv sync --frozen --no-install-project

# 7. Copy the application source code
COPY src/ ./src/
COPY alembic.ini ./

# 8. Start the FastAPI application
EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
