# Ultra-Fast Port Scanner - Docker Image
FROM python:3.11-alpine

# Set metadata
LABEL maintainer="Ultra-Fast Scanner Team <support@ultra-scanner.dev>"
LABEL description="Ultra-Fast Port Scanner with Adaptive Intelligence"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Copy scanner script
COPY ultra_scanner.py /app/ultra_scanner.py

# Make executable
RUN chmod +x /app/ultra_scanner.py

# Create symlink for easier usage
RUN ln -s /app/ultra_scanner.py /usr/local/bin/ultra-scanner

# Set default user (non-root for security)
RUN adduser -D -s /bin/sh scanner
USER scanner

# Set entrypoint
ENTRYPOINT ["python3", "/app/ultra_scanner.py"]

# Default command (help)
CMD ["--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import socket; socket.create_connection(('8.8.8.8', 53), timeout=5)" || exit 1
