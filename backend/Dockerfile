FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY uvicorn_start.sh ./
RUN chmod +x uvicorn_start.sh
ENV API_PORT=8080
EXPOSE 8080
CMD ["./uvicorn_start.sh"]
