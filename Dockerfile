FROM python:3.8-alpine3.13

RUN apk add --no-cache postgresql==13.2-r0

COPY benchmark.py ./

ENTRYPOINT [ "python", "./benchmark.py" ]