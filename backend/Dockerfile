# --- Build Stage ---
FROM astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation for faster startups
ENV UV_COMPILE_BYTECODE=1

# Use a non-root directory for the build
WORKDIR /app

# Install dependencies using the lockfile
# --no-install-project avoids installing the package itself at this layer
# leveraging Docker cache for faster subsequent builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# --- Runtime Stage ---
FROM python:3.13-slim-bookworm

WORKDIR /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy your source code (specifically the src directory)
COPY src ./src
COPY pyproject.toml ./

# If you have a dev/prod toggle, you can handle it via ENV or Entrypoint
ARG deployment=DEV
ENV DEPLOYMENT_MODE=${deployment}

EXPOSE 5000

# Using the venv's uvicorn directly is faster than calling 'uv run' in production
CMD ["uvicorn", "src.portfolio.main:app", "--host", "0.0.0.0", "--port", "5000"]
