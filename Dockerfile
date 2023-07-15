FROM python:3.12.0b4-alpine3.18

WORKDIR /app

COPY ./ /app

RUN apk update && \
    apk add curl rsync

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/app/main.py" ] 