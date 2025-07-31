# Root Dockerfile to run the bot from mybot directory
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements separately for better caching
COPY mybot/requirements.txt ./mybot/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r mybot/requirements.txt

# Copy the rest of the project
COPY mybot ./mybot

# Switch to project directory
WORKDIR /app/mybot

# Start the bot
CMD ["python3", "main.py"]
