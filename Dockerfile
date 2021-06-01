FROM python:3.8.0-slim
COPY dataswati /app
RUN apt-get update \
    && apt install build-essential -y \
    && apt-get clean
RUN pip install --upgrade pip && pip install --user -r /app/requirements.txt
RUN mkdir -p /airflow/xcom && touch /airflow/xcom/return.json

# WORKDIR /app
