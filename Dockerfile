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

# Copy startup script before changing ownership
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Change ownership after copying everything
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start with the startup script
ENTRYPOINT ["/app/startup.sh"]