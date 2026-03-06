FROM python:3.12-slim

WORKDIR /app

COPY client_requirements.txt .
RUN pip install -r client_requirements.txt

COPY client.py .

CMD ["python", "client.py"]
