# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .
# COPY ./.env /app/.env

ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1

# Streamlit settings
ENV STREAMLIT_PORT=8501
ENV STREAMLIT_DISABLE_WATCHDOG_WARNING=true
ENV PYTHONUNBUFFERED=1

# Expose port for ECS
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "scripts/app.py"]
