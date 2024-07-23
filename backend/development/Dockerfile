FROM python:3.11
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /db-init

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.7.1 \
    ENVIRONMENT=production

RUN curl -sSL https://install.python-poetry.org | python3 -
COPY backend/pyproject.toml backend/poetry.lock ./

RUN POETRY_NO_INTERACTION=1 /opt/poetry/bin/poetry install --no-root

COPY backend/backend/db.py ./backend/db.py
COPY backend/development/ ./development

ENTRYPOINT ["python", "-m", "development.db_data"]
