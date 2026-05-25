# Backend

This module provides the FastAPI backend for the meal planning web application.

## Overview

The backend exposes a REST API that serves ingredient and recipe data and generates personalised meal plans using the `GAMealPlanner` engine. Ingredient pricing data is sourced from `priced_ingredients.json` and is used to compute estimated costs for both ingredients and recipes.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/ingredients` | List all ingredients, with optional dietary filters (`gluten_free`, `lactose_free`, `vegetarian`, `vegan`) |
| `GET` | `/api/ingredients/{id}` | Get a single ingredient by ID |
| `GET` | `/api/recipes` | List all recipes, with optional dietary filters |
| `GET` | `/api/recipes/{id}` | Get a single recipe by ID |
| `POST` | `/api/meal-plan` | Generate a meal plan given user preferences and pantry contents |

## Setup and Usage

1. Install dependencies from the root `requirements.txt` (including Uvicorn and FastAPI).
2. Run the `api_setup.py` script to copy the files into the local folder.
3. Run the server from this directory:
   ```bash
   uvicorn main:app
   ```
   The API will be available at the declared API base URL.