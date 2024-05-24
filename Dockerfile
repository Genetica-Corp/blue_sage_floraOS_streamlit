FROM python:3.11-slim AS builder

WORKDIR /app
EXPOSE 8081

COPY requirements.txt requirements.txt
COPY . .
RUN pip install -r requirements.txt

CMD streamlit run Main.py \
    --server.headless true \
    --server.port=8081 \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.baseUrlPath="streamlit-blue-sage" \
    --browser.gatherUsageStats false \
    --browser.serverAddress="0.0.0.0" 
