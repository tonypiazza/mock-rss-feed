# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

EXPOSE 80
CMD ["uv", "run", "python", "-m", "app.main"]
