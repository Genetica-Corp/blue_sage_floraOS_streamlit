FROM python:3.11-slim AS builder

WORKDIR /app
EXPOSE 8081

COPY requirements.txt requirements.txt
COPY . .
RUN pip install -r requirements.txt

# Expose the port streamlit runs on
EXPOSE 8501 

# Run main.py when the container launches
CMD ["streamlit", "run", "Main.py"]
