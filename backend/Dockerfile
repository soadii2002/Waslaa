FROM python:3.11-slim

WORKDIR /app

ARG DEV=false

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000