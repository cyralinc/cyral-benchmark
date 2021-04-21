FROM python:3.8-alpine3.13

COPY entrypoint.sh config.yaml pyproject.toml poetry.lock /
RUN chmod +x entrypoint.sh
COPY pg /pg

RUN apk add --no-cache postgresql==13.2-r0
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

ENTRYPOINT [ "/entrypoint.sh" ]