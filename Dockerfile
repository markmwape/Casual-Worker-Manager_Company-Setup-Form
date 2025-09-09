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

# Create startup script that initializes database then starts the app
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Casual Worker Manager..."\n\
echo "🔧 Initializing database..."\n\
python3 database_init.py\n\
if [ $? -eq 0 ]; then\n\
    echo "✅ Database initialized successfully"\n\
    echo "🌐 Starting web server..."\n\
    exec gunicorn wsgi:app -b 0.0.0.0:$PORT --workers=1 --timeout=300\n\
else\n\
    echo "❌ Database initialization failed"\n\
    exit 1\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# Use the startup script
ENTRYPOINT ["/app/start.sh"]