FROM python:3.12-slim

WORKDIR /app

# Install only required packages for pipeline
RUN pip install --no-cache-dir \
    watchdog>=4.0.0 \
    requests>=2.32.0 \
    python-dotenv>=1.0.0

# Copy pipeline code
COPY automation/ /app/pipeline/automation/
COPY ingestion/ /app/pipeline/ingestion/

# Create data directory
RUN mkdir -p /app/data

# Run watchdog on startup
CMD ["python", "/app/pipeline/automation/watchdog_ingestion.py"]
