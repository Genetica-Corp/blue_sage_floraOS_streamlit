# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV STREAMLIT_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_BROWSER_SERVER_ADDRESS="0.0.0.0"

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port streamlit runs on
EXPOSE 8501 

# Run main.py when the container launches
CMD ["streamlit", "run", "Main.py"]
