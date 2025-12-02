FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . .

# Installer TOUTES les dépendances nécessaires
RUN pip install \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    python-dotenv

EXPOSE 8001

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
