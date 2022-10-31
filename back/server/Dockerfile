FROM python:3.9.14-alpine

ENV PYTHONUNBUFFERED = 1

ADD PSRIS /server/
ADD requirements.txt  /server/

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install -r /server/requirements.txt




EXPOSE 8000:8000/tcp
EXPOSE 8000:8000/udp

WORKDIR /server/
