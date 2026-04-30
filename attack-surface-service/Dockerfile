FROM python:3.11-slim
WORKDIR /app

COPY attack-surface-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY attack-surface-service/ /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]