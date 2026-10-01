FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check
COPY . .

EXPOSE 8000
CMD ["sh", "-c", "python criar_tabelas.py && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
