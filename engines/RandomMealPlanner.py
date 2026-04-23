from random import sample, seed

from engines.MealPlanner import MealPlanner
from models.MealPlanningEnvironment import MealPlanningEnvironment


class RandomMealPlanner(MealPlanner):
    def __init__(self, meal_planning_environment: MealPlanningEnvironment, random_seed: int | None = None):
        """
        The `RandomMealPlanner` class is a simple implementation of the `MealPlanner` abstract class, which generates a meal plan by randomly selecting recipes from the available recipe pool, without any optimisation or consideration of user preferences, pantry stock, or nutritional goals. This serves as a baseline for comparison against more sophisticated meal planning algorithms

        :param meal_planning_environment: the meal planning environment containing recipes, pantry, and user preferences
        :type meal_planning_environment: MealPlanningEnvironment
        """

        super().__init__(meal_planning_environment)

        if random_seed is not None:
            seed(random_seed)

    def generate_meal_plan(self) -> tuple[list[int], float]:
        """
        Generates a meal plan by randomly selecting recipes for each meal slot (breakfast, lunch, dinner) across the week

        :return: a tuple containing the list of selected recipe indices for the meal plan and a placeholder score (0.0) since this planner does not perform any optimisation
        :rtype: tuple[list[int], float]
        """

        num_meals = 7 * 3

        self.best_meal_plan = sample(range(len(self.recipes)), min(num_meals, len(self.recipes)))

        return self.best_meal_plan, 0.0
