FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend files
COPY frontend /app/frontend

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]
