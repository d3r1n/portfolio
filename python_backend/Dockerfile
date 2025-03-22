FROM python:3.13

ARG deployment=DEV

ENV DEPLOYMENT_MODE=${deployment}

WORKDIR /app

COPY pyproject.toml ./

COPY poetry.lock ./

RUN pip install poetry

RUN poetry env use 3.13

RUN poetry install --no-root

# COPY . .

EXPOSE 8000

CMD ["poetry", "run", "fastapi", "run", "python_backend/main.py", "--port", "8000"]