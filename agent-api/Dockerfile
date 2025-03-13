FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the credentials file is accessible
RUN mkdir -p /credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials/service-account.json

# Expose port
EXPOSE 8080

# Command to run the application using gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 agent_api:app 