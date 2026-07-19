# Production image for search indexing and query orchestration.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY services/search/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/search/app ./app

EXPOSE 8040
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8040"]
