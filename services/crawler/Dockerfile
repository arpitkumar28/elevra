# Production image for opportunity and content crawlers.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY services/crawler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/crawler/app ./app

EXPOSE 8010
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
