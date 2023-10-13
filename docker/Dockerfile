############################## Development stage ##############################

FROM python:3.10-slim-bullseye as development

############### Install poetry ###############

ENV \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry" \
    \
    # Here goes our code. Added to make it importable
    PYTHONPATH="/app"

# Add poetry to path to use the "poetry" command
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl \
    && rm -rf /var/lib/apt/lists/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# Since we're in a container, no need to use venvs
RUN poetry config virtualenvs.create false

############### Install dependencies ###############


WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# For development
RUN poetry install

# # For production
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

############### Finish up build ###############

EXPOSE 3000
CMD ["poetry", "run", "manage", "start-reload"]


############################## Production stage ##############################

FROM python:3.10-slim-bullseye

RUN pip install -U pip
RUN pip install uvicorn[standard]

WORKDIR /app
COPY src .
COPY --from=development /app/requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 3000
CMD ["uvicorn", "users_api.app:app", "--host", "0.0.0.0", "--port", "3000", "--log-level", "info"]
