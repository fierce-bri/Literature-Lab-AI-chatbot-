FROM python:3.11-slim

LABEL org.opencontainers.image.title="Literature Lab" \
      org.opencontainers.image.description="Django creative-writing assistant with a browser interface and JSON API" \
      org.opencontainers.image.source="https://github.com/fierce-bri/Literature-Lab-AI-chatbot-"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_DATABASE_PATH=/data/db.sqlite3 \
    PORT=8000

WORKDIR /app

# Install dependencies before copying the application so Docker can reuse
# this layer when source files change but requirements do not.
COPY requirements.txt ./requirements.txt

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt

# Copy the maintained Django project only.
COPY literature_lab ./literature_lab

COPY docker-entrypoint.sh \
    /usr/local/bin/docker-entrypoint.sh

# Prepare writable application and database directories.
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /data \
    && chown -R 10001:10001 /app /data

WORKDIR /app/literature_lab

# Run the application without root privileges.
USER 10001:10001

EXPOSE 8000

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=20s \
    --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/v1/health/', timeout=3).read()"]

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["sh", "-c", "exec gunicorn literature_lab.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 30 --access-logfile - --error-logfile -"]
