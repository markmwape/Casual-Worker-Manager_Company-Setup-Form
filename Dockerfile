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

# Create a startup script as root before switching users
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting Casual Worker Manager..."\n\
echo "📍 Port: ${PORT:-8080}"\n\
echo "🌍 Environment: Production"\n\
echo "👤 User: $(whoami)"\n\
\n\
# Verify app files exist\n\
if [ ! -f "/app/wsgi.py" ]; then\n\
  echo "❌ ERROR: wsgi.py not found!"\n\
  ls -la /app/\n\
  exit 1\n\
fi\n\
\n\
echo "✅ Starting Gunicorn..."\n\
exec gunicorn wsgi:app \\\n\
  --bind 0.0.0.0:${PORT:-8080} \\\n\
  --workers 1 \\\n\
  --worker-class sync \\\n\
  --timeout 300 \\\n\
  --keepalive 65 \\\n\
  --max-requests 1000 \\\n\
  --max-requests-jitter 50 \\\n\
  --log-level info \\\n\
  --access-logfile - \\\n\
  --error-logfile -' > /app/start.sh

# Make script executable and set ownership
RUN chmod +x /app/start.sh

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

CMD ["/app/start.sh"]