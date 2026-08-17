FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout for container logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    
WORKDIR /app

# Install system dependencies (curl is helpful for container healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Streamlit runs on port 8501 by default
EXPOSE 8501

# Healthcheck to verify the web UI is responsive inside the container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# IMPORTANT: Always set --server.address=0.0.0.0. If you bind to 127.0.0.1 (localhost)
# inside a container, traffic coming from outside the container (like your host browser
# or an Ingress controller) will be rejected.