# Casual-Worker-Manager-Company-Setup-Form
FROM python:3.11-slim

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "🚀 Starting Casual Worker Manager..."' >> /app/start.sh && \
    echo 'python3 database_init_minimal.py' >> /app/start.sh && \
    echo 'echo "🌐 Starting web server..."' >> /app/start.sh && \
    echo 'exec gunicorn wsgi:app -b 0.0.0.0:$PORT --workers=1 --timeout=300 --preload' >> /app/start.sh && \
    chmod +x /app/start.sh

# Use the startup script
ENTRYPOINT ["/app/start.sh"]