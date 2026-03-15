# AI Outfit Recommendation Engine

A simple AI-powered web app that recommends 2–3 outfit combinations from your wardrobe based on **occasion**, **weather**, and **style preference**, with reasoning and one suggested item to purchase.

## Features

- **Enter wardrobe items** — Name, category (top, bottom, shoes, etc.), description, color
- **Context** — Occasion, weather (manual or live via city), style preference
- **Recommendations** — 2–3 outfit combinations with short reasoning
- **Suggested purchase** — One item the AI suggests adding to your wardrobe
- **Save wardrobe** — Persist wardrobes and reload them later
- **Weather API** — Optional OpenWeatherMap integration for live weather by city

## Tech Stack

- **Frontend:** React (Vite)
- **Backend:** Python Django + Django REST Framework
- **LLM:** OpenAI API (with fallback when no key is set)

## Quick Start (local)

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (required for AI recommendations)
# Optionally set OPENWEATHER_API_KEY for live weather

python manage.py migrate
python manage.py runserver
```

Backend runs at **http://127.0.0.1:8000**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**. It proxies `/api` to the backend.

### 3. Use the app

1. Add at least one wardrobe item (e.g. “White tee”, Top, “Cotton”, “White”).
2. Optionally add more items.
3. Set occasion (e.g. “Weekend brunch”), weather (or city and click “Get weather”), and style.
4. Click **Get outfit recommendations**.
5. Optionally click **Save wardrobe** to store your list for later.

## API keys

- **OPENAI_API_KEY** — Required for AI-generated outfit suggestions. Get one at [platform.openai.com](https://platform.openai.com). Without it, the app uses a simple rule-based fallback.
- **OPENWEATHER_API_KEY** — Optional. Get one at [openweathermap.org](https://openweathermap.org/api) to use “Get weather” by city.

## Deploy with Docker

From the project root:

```bash
# Create .env with OPENAI_API_KEY (and optionally OPENWEATHER_API_KEY, DJANGO_SECRET_KEY)
docker compose up --build
```

- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000**

The frontend container proxies `/api` to the backend. Wardrobe data is stored in a Docker volume.

## Project structure

```
Outfit_Recommendation/
├── backend/
│   ├── api/              # DRF app: models, views, serializers, services
│   ├── outfit_recommendation/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── WardrobeEntry.jsx
│   │   ├── ContextForm.jsx
│   │   ├── OutfitResults.jsx
│   │   └── SavedWardrobes.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## API overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/wardrobes/` | GET, POST | List or create wardrobes |
| `/api/wardrobes/<id>/` | GET, PUT, PATCH, DELETE | Get or update a wardrobe |
| `/api/wardrobes/<id>/items/` | GET, POST | List or add items |
| `/api/recommend/` | POST | Get outfit recommendations (body: wardrobe_items or wardrobe_id, occasion, weather, style_preference, optional weather_city) |
| `/api/weather/?city=...` | GET | Get weather description for a city |
