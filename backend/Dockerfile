FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    alembic \
    fastapi \
    "psycopg[binary]" \
    pydantic-settings \
    sqlalchemy \
    "uvicorn[standard]"

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
