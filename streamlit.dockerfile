FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.streamlit.txt .
RUN pip install --no-cache-dir -r requirements.streamlit.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]