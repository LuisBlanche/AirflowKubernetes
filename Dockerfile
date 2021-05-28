FROM python:3.8.0-slim
COPY dataswati /app
RUN apt-get update \
    && apt install build-essential -y \
    && apt-get clean
WORKDIR /app
RUN pip install --upgrade pip && pip install --user -r requirements.txt

