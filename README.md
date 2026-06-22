# SOLDIER SUPPORT SYSTEM

## What actually runs

This repo is a 4-part stack:

- `warrior-support-system/` React + Vite frontend
- `warrior-support-system/backend/` Node + Express + MongoDB API
- `warrior-support-system/python-backend/` FastAPI service for voice, facial, sentiment, and financial scoring
- MongoDB for the Node backend

The frontend talks to both backends. The original repo hardcoded `localhost` in several places; the Docker setup now routes everything through the frontend container.

## Local run without Docker

1. Start MongoDB locally.
2. Start the Node backend:
   ```bash
   cd warrior-support-system/backend
   npm install
   npm start
   ```
3. Start the Python backend:
   ```bash
   cd warrior-support-system/python-backend
   pip install -r requirements.txt
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Start the frontend:
   ```bash
   cd warrior-support-system
   npm install
   npm run dev
   ```
5. Open `http://localhost:5173`.

Notes:

- The frontend expects the Node API on port `5000`.
- The Python API listens on port `8000`.
- The Python service downloads large models on first use.

## Docker run

1. Copy `.env.example` to `.env` and set `JWT_SECRET`.
2. Build and start:
   ```bash
   docker compose up --build
   ```
3. Open `http://localhost:8080`.

Initialize MongoDB seed data:

```bash
docker compose exec backend npm run init-db
```

Or run everything in one go:

```bash
docker compose up --build -d && docker compose exec backend npm run init-db
```

## Persistent volumes

The Compose stack keeps state in named volumes:

- `mongo_data` for MongoDB data
- `python_model_data` for explicit Python model downloads under `/app/data/models`
- `python_cache` for Hugging Face, Whisper, and Torch caches
- `python_sessions` for temporary facial-analysis session files

That avoids re-downloading heavyweight models on every rebuild while not masking the Python source package under `python-backend/models/`.
