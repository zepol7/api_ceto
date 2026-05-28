# ── Etapa 1: Base con Python ──────────────────────────────
FROM python:3.11-slim AS base

# Evitar archivos .pyc y buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Etapa 2: Instalar dependencias ───────────────────────
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Etapa 3: Imagen final de producción ──────────────────
FROM dependencies AS production

# Copiar el código fuente
COPY app.py .
COPY tests/ tests/

# Crear usuario no-root (buena práctica de seguridad)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Exponer el puerto de Flask
EXPOSE 5000

# Health check para Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/salud')" || exit 1

# Comando para iniciar la aplicación
CMD ["python", "app.py"]