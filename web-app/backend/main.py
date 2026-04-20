from fastapi import FastAPI
from pydantic import BaseModel

from engines import GAMealPlanner
from models import MealPlanningEnvironment


class UserPreferencesSchema(BaseModel):
    weekly_budget: float = 50.0
    calorie_target_per_day: float = 2500.0
    protein_target_per_day: float = 50.0
    is_vegetarian: bool = False
    is_vegan: bool = False


class MealPlanRequest(BaseModel):
    user_preferences: UserPreferencesSchema = UserPreferencesSchema()


class MealPlanResponse(BaseModel):
    meal_plan: list[list[str]]  # list of days with list of meals for each day
    estimated_cost: float
    calories_per_day: list[float]
    protein_per_day: list[float]
    shopping_list: dict[str, float]  # ingredient name to quantity needed


app = FastAPI(title="GA Meal Planner API")


@app.post("/api/meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(request: MealPlanRequest):
    meal_planning_environment = MealPlanningEnvironment(recipes=[{}])

    ga_meal_planner = GAMealPlanner()

    return MealPlanResponse(meal_plan=[], estimated_cost=0.0, calories_per_day=[], protein_per_day=[], shopping_list={})
