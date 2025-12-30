FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports
EXPOSE 8000 8501

# Create data directory for database
RUN mkdir -p /data

# Use supervisor to run both services
RUN pip install supervisor

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisor
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
