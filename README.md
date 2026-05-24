# Smart, Personalised and Efficient Meal Planning: Using AI to Combat Food Waste

<span style="font-size: 1.5rem; font-weight: bold;">ICT3909 Final Year Project in Artificial Intelligence<br/></span>
<span style="font-size: 1.25rem">By Michael Farrugia</span>

This repository contains the code for my Final Year Project of my Bachelor of Science in Information Technology (Honours) (Artificial Intelligence) at the University of Malta (2025/26), titled "Smart, Personalised and Efficient Meal Planning: Using AI to Combat Food Waste". The project focuses on developing an AI-powered meal planning system that generates personalised weekly meal plans whilst minimising food waste and respecting dietary constraints and budgetary limits.

## Project Structure

Each module has its own README with more detailed documentation.

| Folder | Description |
|--------|-------------|
| `models/` | Core data models shared across the project (recipes, ingredients, pantry, user preferences, etc.) |
| `food_data_extraction/` | Embedding-based semantic search over USDA FoodData Central for nutritional and density lookups |
| `recipe_extraction/` | Pipeline for parsing and structuring raw recipe data from the Epicurious dataset |
| `engines/` | Meal planning engines: ILP, Genetic Algorithm, LLM-based, and Random baseline |
| `evaluation/` | Evaluation framework, metrics, results, and visualisations comparing the planning engines |
| `web-app/` | Full-stack web application (Astro + React frontend, FastAPI backend) |

## Setup and Usage

Given that this project has both Python and JavaScript components, the following system requirements and setup instructions are provided:
- Python 3.11 or higher
- Node.js v24 or higher (for the web application)

### Python Dependencies

Install all Python dependencies from the root of the repository:

```bash
pip install -r requirements.txt
```

### Running the Web Application

See `web-app/README.md` for full setup instructions for the frontend and backend.

### Running the Notebooks

The data pipeline and evaluation are driven by Jupyter notebooks. The recommended order for a full run from scratch is:

1. `food_data_extraction/` — build FAISS indexes (see its README for setup steps)
2. `recipe_extraction/` — parse and structure recipe data
3. `engines/` — test individual planners
4. `evaluation/` — run the full evaluation and export results