FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg and Flask
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir Flask==3.0.0

# Copy application files
COPY app.py .
COPY index.html .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"

# Start the application
CMD ["python3", "app.py"]
