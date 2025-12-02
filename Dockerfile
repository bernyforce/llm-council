# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend Python avec frontend
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copier tout le projet
COPY . .

# Installer les dépendances Python
RUN pip install \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    python-dotenv

# Copier le frontend buildé depuis le stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8001

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
