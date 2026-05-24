from datetime import datetime

import pandas as pd

from engines.utils import get_consumed_stock
from models import MealPlanningEnvironment


class MealPlanner:
    def __init__(self, meal_planning_environment: MealPlanningEnvironment):
        """
        The `MealPlanner` class is an abstract class used by other meal planner implementations, providing common methods and properties for meal planning

        :param meal_planning_environment: the meal planning environment containing recipes, pantry, and user preferences
        :type meal_planning_environment: MealPlanningEnvironment
        """

        self.meal_planning_environment = meal_planning_environment

        self.recipes = self.meal_planning_environment.recipes
        self.pantry_stock = self.meal_planning_environment.pantry.stock
        self.days_until_expiry = self.meal_planning_environment.pantry.get_days_until_expiry(datetime.now())
        self.ingredient_costs = self.meal_planning_environment.ingredient_costs
        self.preferences = self.meal_planning_environment.preferences

        self.best_meal_plan: list[int] = []
        self.consumed_stock: dict[str, float] = {}

    def generate_meal_plan(self) -> tuple[list[int], float]:
        raise NotImplementedError("Meal plan generation logic is not implemented yet")

    def get_pantry_consumption(self) -> pd.DataFrame:
        """
        Calculates how much of each pantry ingredient is consumed across the best meal plan, and returns a DataFrame showing available, consumed, and unused quantities along with days until expiry

        :return: DataFrame with columns "Ingredient", "Available", "Consumed", "Unused", and "Expires in"
        :rtype: pd.DataFrame
        """

        meal_plan_recipes = [
            [self.recipes[int(index)] for index in self.best_meal_plan[i : i + 3]]
            for i in range(0, len(self.best_meal_plan), 3)
        ]

        self.consumed_stock = get_consumed_stock(meal_plan_recipes, self.pantry_stock)

        pantry_data = []

        for ingredient in self.meal_planning_environment.pantry.ingredients:
            available = self.pantry_stock[ingredient.name]
            used = self.consumed_stock.get(ingredient.name, 0)
            unused = max(0, available - used)
            days = self.days_until_expiry[ingredient.name]
            expiry_str = str(days) + "d"

            pantry_data.append(
                {
                    "Ingredient": ingredient.name,
                    "Available": available,
                    "Consumed": used,
                    "Unused": unused,
                    "Expires in": expiry_str,
                }
            )

        pantry_data_df = pd.DataFrame(pantry_data)

        return pantry_data_df

    def get_shopping_list(self) -> tuple[pd.DataFrame, int, float]:
        """
        Generates a shopping list based on the best meal plan, considering pantry stock and ingredient costs, and returns a DataFrame with the shopping list along with total number of ingredients to buy and total estimated cost

        :return: tuple of (shopping list DataFrame with columns "Ingredient", "Quantity to Buy (g)", and "Cost (€)", total number of ingredients to buy, total estimated cost)
        :rtype: tuple[pd.DataFrame, int, float]
        """

        shopping_list = {}
        consumed_from_pantry: dict[str, float] = dict.fromkeys(self.pantry_stock, 0.0)

        for index in self.best_meal_plan:
            recipe = self.recipes[int(index)]

            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = self.pantry_stock.get(ingredient_name, 0) - consumed_from_pantry.get(ingredient_name, 0.0)
                from_pantry = max(0.0, min(available, quantity_needed))
                to_buy = quantity_needed - from_pantry
                consumed_from_pantry[ingredient_name] = consumed_from_pantry.get(ingredient_name, 0.0) + from_pantry
                if to_buy > 0:
                    shopping_list[ingredient_name] = shopping_list.get(ingredient_name, 0.0) + to_buy

        shopping_data = [
            {
                "Ingredient": name,
                "Quantity to Buy (g)": round(qty, 1),
                "Cost (€)": round((qty / 100.0) * self.ingredient_costs.get(name, 1.0), 2),
            }
            for name, qty in sorted(shopping_list.items())
        ]

        shopping_df = pd.DataFrame(shopping_data)

        total_cost = shopping_df["Cost (€)"].sum()
        total_row = pd.DataFrame([{"Ingredient": "TOTAL", "Quantity to Buy (g)": "", "Cost (€)": round(total_cost, 2)}])
        shopping_df = pd.concat([shopping_df, total_row], ignore_index=True)

        return shopping_df, len(shopping_data), total_cost

    def get_daily_nutrition(self) -> pd.DataFrame:
        """
        Calculates the total calories and protein for each day in the best meal plan, and returns a DataFrame showing daily calories, daily protein, and how they compare to the user's targets

        :return: DataFrame with columns "Day", "Calories", "Protein (g)", "Calorie Target", "Protein Target (g)", "Calorie Difference", and "Protein Difference"
        :rtype: pd.DataFrame
        """

        num_days = len(self.best_meal_plan) // 3

        daily_nutrition_data = []

        for day in range(num_days):
            day_indices = self.best_meal_plan[day * 3 : day * 3 + 3]

            daily_calories = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
            )
            daily_protein = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
            )

            calorie_diff = daily_calories - self.preferences.calorie_target_per_day
            protein_diff = daily_protein - self.preferences.protein_target_per_day

            daily_nutrition_data.append(
                {
                    "Day": f"Day {day + 1}",
                    "Calories": f"{round(daily_calories, 1)} kcal",
                    "Protein": f"{round(daily_protein, 1)} g",
                    "Δ Calories and Target Calories": f"{round(calorie_diff, 1)} kcal",
                    "Δ Protein and Target Protein": f"{round(protein_diff, 1)} g",
                }
            )

        daily_nutrition_df = pd.DataFrame(daily_nutrition_data, index=[d["Day"] for d in daily_nutrition_data]).drop(
            columns=["Day"]
        )

        return daily_nutrition_df

    def get_meal_plan_recipes(self) -> pd.DataFrame:
        """
        Returns a DataFrame showing the names of the meals planned for each day based on the best meal plan

        :return: DataFrame with columns "Day", "Meal 1", "Meal 2", and "Meal 3"
        :rtype: pd.DataFrame
        """

        meal_plan = []

        for day in range(7):
            meal_indices = self.best_meal_plan[day * 3 : day * 3 + 3]
            meal_names = [self.recipes[int(index)].name for index in meal_indices]
            meal_plan.append(
                {
                    "Day": day + 1,
                    "Meal 1": meal_names[0],
                    "Meal 2": meal_names[1],
                    "Meal 3": meal_names[2],
                }
            )

        meal_plan_df = pd.DataFrame(meal_plan, index=[f"Day {d['Day']}" for d in meal_plan]).drop(columns=["Day"])

        return meal_plan_df
