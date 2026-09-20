# Production-ready Dockerfile for CyberCase Framework FastAPI Backend
# Using ./backend context for build
FROM python:3.11-slim

WORKDIR /app

# Thai fonts for the formal export, and the Pango/Cairo stack WeasyPrint
# lays text out with. fontconfig finds the fonts on its own from here.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fonts-noto-core \
        fonts-tlwg-garuda-ttf \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libharfbuzz-subset0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy backend application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Expose FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
