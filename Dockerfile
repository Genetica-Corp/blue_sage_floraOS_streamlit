FROM python:3.11-slim AS builder

WORKDIR /app
EXPOSE 8081

COPY requirements.txt requirements.txt
COPY secrets.toml secrets.toml
COPY . .
RUN chmod 644 secrets.toml
RUN pip install -r requirements.txt


CMD streamlit run main.py \
    --server.headless true \
    --server.port=8081 \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false \
    --browser.serverAddress="localhost" 
