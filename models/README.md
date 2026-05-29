# Models

This module contains the core data models used throughout the project. These models represent the domain objects that are shared across recipe extraction, meal planning, and evaluation.

## Models

- `NutritionalInformation`: represents the complete nutritional profile of an ingredient or recipe, including macronutrients (calories, carbohydrates, protein, fat, saturated fat, sugar), micronutrients (fibre, sodium), and dietary compliance flags (vegan, vegetarian, gluten-free, lactose-free).
- `DietaryTag`: an enumeration of dietary compliance tags (`VEGAN`, `VEGETARIAN`, `GLUTEN_FREE`, `LACTOSE_FREE`) used to categorise ingredients and recipes.
- `Ingredient`: represents a basic ingredient with a name and its nutritional information per 100 grams.
- `PantryIngredient`: extends `Ingredient` with an estimated expiration date, used to track ingredient freshness within a pantry.
- `Pantry`: represents a collection of `PantryIngredient` objects with their available quantities in grams, used as a starting inventory for meal planning.
- `Recipe`: represents a recipe with a name, a mapping of ingredient names to required quantities (in grams), dietary tags, and step-by-step instructions. Nutritional information for the recipe as a whole is computed by aggregating per-ingredient nutritional data scaled by quantity.
- `UserPreferences`: captures user dietary constraints and nutritional targets used to guide fitness evaluation during meal planning, including weekly budget, daily calorie and protein targets, and dietary restrictions.
- `MealPlanningEnvironment`: encapsulates all data required for meal planning. This includes available recipes, pantry stock, user preferences, and ingredient costs. It also handles loading recipes from JSON and automatically filters ingredients and recipes based on the user's dietary preferences (e.g., gluten-intolerant user preferences result in all gluten-containing recipes and ingredients being excluded).