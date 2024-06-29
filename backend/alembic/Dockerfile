FROM python:3.11.2-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION="1.7.1" \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN python3 -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /db-init

COPY backend/pyproject.toml backend/poetry.lock ./
RUN $POETRY_HOME/bin/poetry install --only main

COPY backend/alembic.ini ./
COPY backend/alembic ./alembic

ENTRYPOINT ["/db-init/.venv/bin/alembic", "upgrade", "head"]
#ENTRYPOINT ["python", "-c", "import time; time.sleep(600)"]