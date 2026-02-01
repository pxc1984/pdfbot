FROM python:3.12-alpine3.21

WORKDIR /usr/src/app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY bot ./bot

RUN uv pip install --system --no-cache -e .

COPY . .

CMD [ "python", "-m", "bot.main" ]
