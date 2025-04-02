# Use Python Base Image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy application files
COPY kafka_to_postgres.py kafka_to_postgres_batch.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Kafka Consumer service
CMD ["python", "kafka_to_postgres_batch.py"]
