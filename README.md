# Personal Finance

A personal finance and shared-expense application, built incrementally as a portfolio project.

## Current Stack

- Python 3.14
- FastAPI and Pydantic
- SQLAlchemy and PostgreSQL
- Alembic
- pytest and Ruff
- Docker Compose

## Local Development

From the `backend/` directory, create and activate a virtual environment:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Copy the example environment file:

```bash
cp .env.example .env
```

Start PostgreSQL with Docker Compose:

```bash
docker compose up -d postgres
```

Run the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. The health endpoint is `GET /health`.

Run the tests:

```bash
pytest
```