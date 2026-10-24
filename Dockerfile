
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
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

# Run as a normal user, not as root.
RUN useradd --create-home --uid 1000 app && chown app:app /app
USER app

# 5. Copy dependency definitions first
COPY --chown=app:app pyproject.toml uv.lock ./

# 6. Install locked dependencies without installing the project itself
RUN uv sync --frozen --no-install-project

# 7. Copy the application source code
COPY --chown=app:app src/ ./src/
COPY --chown=app:app alembic.ini ./

# 8. Start the FastAPI application
EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
