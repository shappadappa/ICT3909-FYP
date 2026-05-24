# Web App

This module provides the full-stack web application for the meal planning system, consisting of an Astro + React frontend and a FastAPI backend.

## Overview

The web application allows users to browse available ingredients and recipes, specify their dietary preferences and pantry contents, and generate a personalised weekly meal plan. The frontend communicates with the backend REST API, which uses the `GAMealPlanner` engine to produce meal plans.

- `frontend/`: built with [Astro](https://astro.build) and [React](https://react.dev), styled with [Tailwind CSS](https://tailwindcss.com), and uses [nanostores](https://github.com/nanostores/nanostores) for client-side state management.
- `backend/`: a [FastAPI](https://fastapi.tiangolo.com/) server exposing a REST API for ingredient and recipe data, and meal plan generation.

Each subfolder has its own README with further details.

## Setup and Usage

### Backend

1. Install Python dependencies from the root `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the `api_setup.py` script inside `backend/` to copy the required data files into the local folder.
3. Start the API server:
   ```bash
   cd backend
   uvicorn main:app
   ```
   The API will be available at `http://localhost:8000`.

### Frontend

Ensure [Node.js](https://nodejs.org/en) v24 or higher is installed. Then, from the `frontend/` directory:

1. Install dependencies:
   ```bash
   npm i
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.