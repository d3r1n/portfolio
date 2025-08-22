FROM python:3.13-slim

ARG deployment=DEV
ENV DEPLOYMENT_MODE=${deployment}

WORKDIR /app

# Copy project metadata first (for caching)
COPY pyproject.toml uv.lock ./

# Install uv
RUN pip install --upgrade pip \
    && pip install uv

# Install dependencies only (not the project itself yet)
RUN uv sync --locked --no-install-project

# Copy source code
COPY . .

EXPOSE 5000

# Run app with uv
CMD ["uv", "run", "uvicorn", "python_backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
