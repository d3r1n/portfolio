FROM python:3.13

ARG deployment=DEV
ENV DEPLOYMENT_MODE=${deployment}

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry 
RUN poetry config virtualenvs.create false 
RUN poetry install --no-root

COPY . .

EXPOSE 5000

CMD ["poetry", "run", "uvicorn", "python_backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
