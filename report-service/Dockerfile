FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

COPY report-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY report-service/ /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005"]