import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from engines import GAMealPlanner
from models import MealPlanningEnvironment
from models.NutritionalInformation import NutritionalInformation
from models.Pantry import Pantry
from models.PantryIngredient import PantryIngredient
from models.UserPreferences import UserPreferences

DATA_DIR = Path(__file__).parent

with open(DATA_DIR / "supplemented_structured_ingredients.json") as file:
    INGREDIENTS = json.load(file)

with open(DATA_DIR / "supplemented_structured_recipes.json") as file:
    RECIPES = json.load(file)

with open(DATA_DIR / "best_ga_meal_planner_hyperparameters.json") as file:
    BEST_GA_HYPERPARAMETERS = json.load(file)

with open(DATA_DIR / "priced_ingredients.json") as file:
    _raw_priced = json.load(file)

_ingredient_id_to_name = {ingredient["id"]: ingredient["name"] for ingredient in INGREDIENTS}
_ingredient_id_to_price: dict[str, float] = dict(_raw_priced.items())

# priced ingredients is {id: price_per_100_grams}
# convert to {name: price_per_100_grams}
PRICED_INGREDIENTS = {
    _ingredient_id_to_name[ingredient_id]: price_per_100g
    for ingredient_id, price_per_100g in _raw_priced.items()
    if ingredient_id in _ingredient_id_to_name
}


def _with_ingredient_cost(ingredient: dict) -> dict:
    price = _ingredient_id_to_price.get(ingredient["id"])
    return {**ingredient, "price_per_100g": price}


def _with_recipe_cost(recipe: dict) -> dict:
    cost = sum(
        (entry["quantity"] / 100.0) * PRICED_INGREDIENTS.get(entry["ingredient"], 0.0)
        for entry in recipe["ingredients"]
    )
    return {**recipe, "estimated_cost": round(cost, 2)}


# schema and other type declarations
class IngredientOrRecipeQuerySchema(BaseModel):
    gluten_free: bool | None = None
    lactose_free: bool | None = None
    vegetarian: bool | None = None
    vegan: bool | None = None
    ids: list[str] | None = None


class UserPreferencesSchema(BaseModel):
    weekly_budget: float = 50.0
    calorie_target_per_day: float = 2500.0
    protein_target_per_day: float = 50.0
    is_vegetarian: bool = False
    is_vegan: bool = False
    requires_gluten_free: bool = False
    requires_lactose_free: bool = False
    pantry_weight: float = 1.0
    waste_weight: float = 1.0
    budget_weight: float = 1.0
    dietary_weight: float = 1.0


class PantryItemSchema(BaseModel):
    id: str
    ingredient_name: str
    quantity_grams: float
    expiry_date: str | None = None  # ISO format date string "YYYY-MM-DD"


class MealPlanRequest(BaseModel):
    user_preferences: UserPreferencesSchema = UserPreferencesSchema()
    pantry_items: list[PantryItemSchema] = []
    num_days: int = 7
    meals_per_day: int = 3
    num_generations: int = 500


class MealPlanResponse(BaseModel):
    meal_plan: list[list[str]]  # list of days with list of meals for each day
    fitness_score: float
    estimated_cost: float
    calories_per_day: list[float]
    protein_per_day: list[float]
    shopping_list: list[dict[str, str | float]]  # list of ingredients with name, quantity to buy (g) and cost (€)


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="GA Meal Planner API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ict-3909-fyp.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ingredients")
@limiter.limit("60/minute")
async def get_ingredients(
    request: Request,
    body: IngredientOrRecipeQuerySchema = Depends(),
):
    filtered_ingredients = INGREDIENTS

    if body.gluten_free:
        filtered_ingredients = [
            ingredient for ingredient in filtered_ingredients if ingredient["nutritional_information"]["is_gluten_free"]
        ]
    if body.lactose_free:
        filtered_ingredients = [
            ingredient
            for ingredient in filtered_ingredients
            if ingredient["nutritional_information"]["is_lactose_free"]
        ]
    if body.vegetarian:
        filtered_ingredients = [
            ingredient for ingredient in filtered_ingredients if ingredient["nutritional_information"]["is_vegetarian"]
        ]
    if body.vegan:
        filtered_ingredients = [
            ingredient for ingredient in filtered_ingredients if ingredient["nutritional_information"]["is_vegan"]
        ]
    if body.ids:
        filtered_ingredients = [ingredient for ingredient in filtered_ingredients if ingredient["id"] in body.ids]

    return [_with_ingredient_cost(i) for i in filtered_ingredients]


@app.get("/api/ingredients/{ingredient_id}")
@limiter.limit("60/minute")
async def get_ingredient(request: Request, ingredient_id: str):
    matched_ingredient = next((ingredient for ingredient in INGREDIENTS if ingredient["id"] == ingredient_id), None)

    if matched_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return _with_ingredient_cost(matched_ingredient)


@app.get("/api/recipes")
@limiter.limit("60/minute")
async def get_recipes(
    request: Request,
    body: IngredientOrRecipeQuerySchema = Depends(),
):
    filtered_recipes = RECIPES

    if body.gluten_free:
        filtered_recipes = [recipe for recipe in filtered_recipes if "GLUTEN_FREE" in recipe["dietary_tags"]]
    if body.lactose_free:
        filtered_recipes = [recipe for recipe in filtered_recipes if "LACTOSE_FREE" in recipe["dietary_tags"]]
    if body.vegetarian:
        filtered_recipes = [recipe for recipe in filtered_recipes if "VEGETARIAN" in recipe["dietary_tags"]]
    if body.vegan:
        filtered_recipes = [recipe for recipe in filtered_recipes if "VEGAN" in recipe["dietary_tags"]]
    if body.ids:
        filtered_recipes = [recipe for recipe in filtered_recipes if recipe["id"] in body.ids]

    return [_with_recipe_cost(r) for r in filtered_recipes]


@app.get("/api/recipes/{recipe_id}")
@limiter.limit("60/minute")
async def get_recipe(request: Request, recipe_id: str):
    matched_recipe = next((recipe for recipe in RECIPES if recipe["id"] == recipe_id), None)

    if matched_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return _with_recipe_cost(matched_recipe)


@app.post("/api/meal-plan", response_model=MealPlanResponse)
@limiter.limit("5/minute")
def generate_meal_plan(request: Request, body: MealPlanRequest):
    user_preferences = UserPreferences(
        weekly_budget=body.user_preferences.weekly_budget,
        calorie_target_per_day=body.user_preferences.calorie_target_per_day,
        protein_target_per_day=body.user_preferences.protein_target_per_day,
        is_vegetarian=body.user_preferences.is_vegetarian,
        is_vegan=body.user_preferences.is_vegan,
        requires_gluten_free=body.user_preferences.requires_gluten_free,
        requires_lactose_free=body.user_preferences.requires_lactose_free,
    )

    pantry = Pantry()

    for item in body.pantry_items:
        ingredient_data = next((ingredient for ingredient in INGREDIENTS if ingredient["id"] == item.id), None)

        if ingredient_data is None:
            raise HTTPException(status_code=400, detail=f"Ingredient with ID '{item.id}' not found")

        nutritional_information = NutritionalInformation(**ingredient_data["nutritional_information"])

        expiry = datetime.fromisoformat(item.expiry_date) if item.expiry_date else datetime(9999, 12, 31)
        pantry_ingredient = PantryIngredient(
            name=ingredient_data["name"],
            nutritional_information=nutritional_information,
            estimated_expiration_date=expiry,
        )
        pantry.add(pantry_ingredient, item.quantity_grams)

    meal_planning_environment = MealPlanningEnvironment(
        preferences=user_preferences,
        pantry=pantry,
        ingredient_costs=PRICED_INGREDIENTS,
    )
    meal_planning_environment.load_recipes_from_json(str(DATA_DIR / "supplemented_structured_recipes.json"))

    planner = GAMealPlanner(
        meal_planning_environment=meal_planning_environment,
        pantry_weight=body.user_preferences.pantry_weight,
        waste_weight=body.user_preferences.waste_weight,
        budget_weight=body.user_preferences.budget_weight,
        dietary_weight=body.user_preferences.dietary_weight,
    )
    best_plan_indices, fitness = planner.generate_meal_plan(
        num_days=body.num_days,
        meals_per_day=body.meals_per_day,
        num_generations=body.num_generations,
        generation_print_interval=None,
        **BEST_GA_HYPERPARAMETERS,
    )

    num_days = body.num_days
    meals_per_day = body.meals_per_day

    meal_plan_ids = [
        [
            meal_planning_environment.recipes[index].id
            for index in best_plan_indices[day * meals_per_day : (day + 1) * meals_per_day]
        ]
        for day in range(num_days)
    ]

    calories_per_day = [
        sum(
            meal_planning_environment.recipes[index].nutritional_information.calories or 0.0
            for index in best_plan_indices[day * meals_per_day : (day + 1) * meals_per_day]
        )
        for day in range(num_days)
    ]
    protein_per_day = [
        sum(
            meal_planning_environment.recipes[index].nutritional_information.protein or 0.0
            for index in best_plan_indices[day * meals_per_day : (day + 1) * meals_per_day]
        )
        for day in range(num_days)
    ]

    shopping_df, _, estimated_cost = planner.get_shopping_list()
    shopping_list = [
        {
            "ingredient_name": row["Ingredient"],
            "quantity_grams": float(row["Quantity to Buy (g)"]),
            "estimated_cost": float(row["Cost (€)"]),
        }
        for _, row in shopping_df.iterrows()
        if row["Ingredient"] != "TOTAL"
    ]

    return MealPlanResponse(
        meal_plan=meal_plan_ids,
        fitness_score=round(fitness, 4),
        estimated_cost=round(estimated_cost, 2),
        calories_per_day=[round(c, 1) for c in calories_per_day],
        protein_per_day=[round(p, 1) for p in protein_per_day],
        shopping_list=shopping_list,
    )
