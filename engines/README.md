# Engines

This module provides the core meal planning engines, including:
- `ILPMealPlanner`: an exact optimisation engine implemented using Integer Linear Programming (ILP) via `scipy`. This engine guarantees optimal meal plans but can be computationally expensive for larger scenarios.
- `GAMealPlanner`: a heuristic engine implemented using a Genetic Algorithm (GA) via the `pygad` library. This engine provides near-optimal meal plans much faster than ILP, especially for larger scenarios, but does not guarantee optimality.
- `RandomMealPlanner`: a baseline engine that generates random meal plans without optimisation. This serves as a lower bound for performance comparison.
- `LLMMealPlanner`: a heuristic engine that uses a Large Language Model (LLM) to generate meal plans based on specified, structured prompts, making use of OpenAI's GPT models.

## Notebooks

A notebook is provided for each engine, demonstrating how to use it to generate meal plans for a given test scenario. These notebooks are aptly named `test_{engine_name}.ipynb` (e.g. `test_ILPMealPlanner.ipynb`).

Another notebook is provided, `tuning_GAMealPlanner.ipynb`, which, by using an `Optuna` study, tunes the hyperparameters of the `GAMealPlanner` to find the best configuration for generating high-quality meal plans. This outputs a set of optimal hyperparameters that can be found in `best_ga_meal_planner_hyperparameters.json`.

## Other Files

- The fitness function used by both the `ILPMealPlanner` and `GAMealPlanner` is implemented in `fitness_score.py`. This function computes a fitness score for a given meal plan based on how well it meets the specified nutritional requirements, budgetary constraints, and how well it reduces food waste and makes best use of the pantry.
- Functions reused by many engines, and also during evaluation, are declared in `utils.py`. This includes helper functions for preparing meal planning environments and parsing data.
- The specific, template prompt used by the `LLMMealPlanner` to generate meal plans is stored in `LLMMealPlannerPrompt.txt`. This prompt is designed to be structured and detailed, to elicit high-quality meal plans from the LLM, and is supplemented with specific context when initialising the planner.