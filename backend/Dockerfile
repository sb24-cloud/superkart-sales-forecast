FROM python:3.9-slim

WORKDIR /app

# Install dependencies first so this layer is cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# Gunicorn with 4 workers, listening on all interfaces on port 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "--timeout", "120", "app:superkart_api"]
