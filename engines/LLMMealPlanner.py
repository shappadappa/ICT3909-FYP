from engines.MealPlanner import MealPlanner
from models import MealPlanningEnvironment


class LLMMealPlanner(MealPlanner):
    def __init__(self, meal_planning_environment: MealPlanningEnvironment):
        """
        The `LLMMealPlanner` class is an implementation of the `MealPlanner` abstract class that uses a large language model (LLM) to generate a meal plan. The LLM is prompted with detailed information about the available recipes, the user's pantry stock, and their preferences, and is tasked with selecting an optimal combination of recipes for the week

        :param meal_planning_environment: the meal planning environment containing recipes, pantry, and user preferences
        :type meal_planning_environment: MealPlanningEnvironment
        """

        super().__init__(meal_planning_environment)

        with open("./LLMMealPlannerPrompt.txt", "r", encoding="utf-8") as prompt:
            self.prompt = prompt.read()

        # add available recipes, pantry stock, and user preferences to the prompt in a structured format

        self.prompt += "\n---\nAVAILABLE RECIPES:\n"

        for index, recipe in enumerate(self.recipes):
            self.prompt += f"{index}: {recipe.to_dict()}\n"

    def generate_meal_plan(self) -> tuple[list[int], float]:
        """
        Generates a meal plan by prompting a large language model with the provided information about recipes, pantry, and user preferences

        :return: a tuple containing the list of selected recipe indices for the meal plan and a placeholder score (0.0) since this planner does not perform explicit optimisation
        :rtype: tuple[list[int], float]
        """

        # TODO: implement LLM prompting logic to generate meal plan based on self.prompt and parse the response to extract selected recipe indices

        return self.best_meal_plan, 0.0
