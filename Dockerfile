FROM node:18 AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install uv
COPY . .
RUN uv sync --frozen
COPY --from=frontend-build /app/dist /app/frontend/dist
EXPOSE 8001
CMD ["uv", "run", "python", "-m", "backend.main"]
