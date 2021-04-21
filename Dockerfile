FROM python:3.8-alpine3.13

RUN apk add --no-cache postgresql==13.2-r0
RUN pip install poetry && poetry install

COPY entrypoint.sh /
RUN chmod +x entrypoint.sh
COPY pg /pg

ENTRYPOINT [ "/entrypoint.sh" ]