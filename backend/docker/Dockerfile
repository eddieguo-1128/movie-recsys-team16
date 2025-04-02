FROM python:3.9-slim

RUN apt-get update && apt-get install -y gcc build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8081

CMD ["python", "run.py"]
