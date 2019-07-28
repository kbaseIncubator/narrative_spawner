FROM python:3-slim

RUN apt-get -y update && apt-get -y install curl gcc
ADD requirements.txt .

RUN pip install -r requirements.txt
ADD . /app
WORKDIR /app



