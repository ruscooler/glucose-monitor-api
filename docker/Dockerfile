FROM python:3.11

RUN mkdir /app
WORKDIR /app

COPY ../pyproject.toml poetry.lock ./

RUN apt-get update -y && apt-get install -y \
    libdmtx0b \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY ../src .


COPY docker/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

COPY docker/wait-for-it.sh docker/wait-for-it.sh
RUN chmod +x docker/wait-for-it.sh

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
