FROM python:3.8-alpine3.13

RUN apk add --no-cache postgresql==13.2-r0
COPY requirements.txt /
RUN pip install -r requirements.txt

COPY entrypoint.sh config.yaml /
RUN chmod +x entrypoint.sh
COPY pg /pg

ENTRYPOINT [ "/entrypoint.sh" ]