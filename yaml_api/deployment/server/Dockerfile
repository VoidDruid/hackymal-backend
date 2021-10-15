ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION:-3.8}-slim-buster as prod

ENV POETRY_VERSION=1.1.5
RUN pip install "poetry==$POETRY_VERSION" && poetry config virtualenvs.create false

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE=on
ENV PYTHONFAULTHANDLER=on
ENV PYTHONUNBUFFERED=on

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependencies
ARG RUN_LEVEL=production
ENV RUN_LEVEL=${RUN_LEVEL}
COPY pyproject.toml poetry.loc[k] /opt/app/
WORKDIR /opt/app
RUN poetry install $(if [ "${RUN_LEVEL}" = "production" ]; then echo "--no-dev"; fi ) --no-interaction --no-ansi -vvv

# Application
COPY settings ./settings
COPY dataplane ./dataplane
COPY common ./common
COPY service ./service
COPY domain ./domain

COPY deployment/pre_start.py ./
COPY deployment/server/server.sh deployment/server/gunicorn_conf.py ./
RUN chmod +x server.sh

ARG APP_MODULE=service:app
ENV APP_MODULE=${APP_MODULE}
EXPOSE 8080
CMD ["./server.sh"]

# --- Development image ---

FROM prod as dev

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--reload", "service:app"]
