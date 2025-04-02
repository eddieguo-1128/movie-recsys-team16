# Use Python base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy app files
COPY kafka_to_victoriametrics.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the service
CMD ["python", "kafka_to_victoriametrics.py"]
