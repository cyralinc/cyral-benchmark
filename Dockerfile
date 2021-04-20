FROM python:3.8-alpine3.13

RUN apk add --no-cache postgresql==13.2-r0

COPY scripts /scripts
WORKDIR /scripts

ENTRYPOINT [ "python" ]