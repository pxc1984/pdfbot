FROM python:3.12-alpine3.21

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir uv
RUN uv pip install --system --no-cache -e .

CMD [ "python", "./main.py" ]
