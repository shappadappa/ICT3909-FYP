import json

from models.DietaryTag import DietaryTag
from models.NutritionalInformation import NutritionalInformation
from models.Pantry import Pantry
from models.Recipe import Recipe
from models.UserPreferences import UserPreferences


class MealPlanningEnvironment:
    def __init__(
        self,
        recipes: list[Recipe] = [],
        pantry: Pantry = Pantry(),
        preferences: UserPreferences = UserPreferences(),
        ingredient_costs: dict[str, float] = {},
    ):
        """
        The `MealPlanningEnvironment` class encapsulates all the data and information needed for meal planning,
        including recipes, pantry stock, user preferences, and ingredient costs.

        :param recipes: list of available recipes to choose from (default = empty list)
        :type recipes: list[Recipe]
        :param pantry: the pantry containing available ingredients and their quantities (default = empty Pantry)
        :type pantry: Pantry
        :param preferences: user dietary preferences and restrictions (default = no restrictions)
        :type preferences: UserPreferences
        :param ingredient_costs: dictionary mapping ingredient names to their costs per unit (default = empty dict)
        :type ingredient_costs: dict[str, float]
        """

        self.recipes = recipes
        self.pantry = pantry
        self.preferences = preferences
        self.ingredient_costs = ingredient_costs

        self._check_ingredient_costs()

        self.ingredient_nutritional_information_lookup: dict[str, NutritionalInformation] = {}

        self._filter_ingredients_by_dietary_preferences()
        self._filter_recipes_by_dietary_preferences()

    def load_recipes_from_json(self, filepath: str):
        self.recipes = []

        with open(filepath, "r", encoding="utf-8") as f:
            recipes_data = json.load(f)

        for item in recipes_data:
            ingredients = {ingredient["ingredient"]: ingredient["quantity"] for ingredient in item["ingredients"]}
            dietary_tags = self._parse_dietary_tags(item.get("dietary_tags", []))

            recipe = Recipe(
                name=item["name"].strip(),
                ingredients=ingredients,
                dietary_tags=dietary_tags,
                instructions=item.get("instructions", []),
                id=item["id"] if "id" in item else None,
            )

            recipe.nutritional_information = self._parse_nutritional_information(item["nutritional_information"])

            self.recipes.append(recipe)

        self._filter_recipes_by_dietary_preferences()
        self._check_ingredient_costs()

    def _parse_dietary_tags(self, tags: list[str]) -> list[DietaryTag]:
        tag_map = {
            "VEGETARIAN": DietaryTag.VEGETARIAN,
            "VEGAN": DietaryTag.VEGAN,
            "GLUTEN_FREE": DietaryTag.GLUTEN_FREE,
            "LACTOSE_FREE": DietaryTag.LACTOSE_FREE,
        }
        return [tag_map[tag] for tag in tags if tag in tag_map]

    def _parse_nutritional_information(self, nutritional_information_dict: dict) -> NutritionalInformation:
        return NutritionalInformation(
            calories=nutritional_information_dict.get("calories"),
            carbohydrates=nutritional_information_dict.get("carbohydrates"),
            sugar=nutritional_information_dict.get("sugar"),
            protein=nutritional_information_dict.get("protein"),
            fat=nutritional_information_dict.get("fat"),
            saturated_fat=nutritional_information_dict.get("saturated_fat"),
            fiber=nutritional_information_dict.get("fiber"),
            sodium=nutritional_information_dict.get("sodium"),
            is_gluten_free=nutritional_information_dict.get("is_gluten_free"),
            is_lactose_free=nutritional_information_dict.get("is_lactose_free"),
            is_vegetarian=nutritional_information_dict.get("is_vegetarian"),
            is_vegan=nutritional_information_dict.get("is_vegan"),
        )

    def _filter_ingredients_by_dietary_preferences(self):
        """
        Filters the ingredients stored in the pantry based on the user's dietary preferences.

        For example, if the user is vegan, all non-vegan ingredients will be filtered out
        """

        names_to_remove = []

        for name, ingredient in self.pantry._ingredients.items():
            ni = ingredient.nutritional_information

            if (
                (self.preferences.is_vegan and not ni.is_vegan)
                or (self.preferences.is_vegetarian and not ni.is_vegetarian)
                or (self.preferences.requires_gluten_free and not ni.is_gluten_free)
                or (self.preferences.requires_lactose_free and not ni.is_lactose_free)
            ):
                names_to_remove.append(name)

        for name in names_to_remove:
            del self.pantry._ingredients[name]
            del self.pantry._quantities[name]

    def _filter_recipes_by_dietary_preferences(self):
        """
        Filters the recipes stored in the environment based on the user's dietary preferences.

        For example, if the user is vegan, all non-vegan recipes will be filtered out
        """

        self.recipes = [
            recipe
            for recipe in self.recipes
            if (not self.preferences.is_vegan or recipe.is_vegan)
            and (not self.preferences.is_vegetarian or recipe.is_vegetarian)
            and (not self.preferences.requires_gluten_free or recipe.is_gluten_free)
            and (not self.preferences.requires_lactose_free or recipe.is_lactose_free)
        ]

    def _check_ingredient_costs(self):
        """
        Checks if all ingredients used in the recipes have a cost defined in the meal planning environment.

        If any ingredient is missing a cost, a warning is printed
        """

        num_missing_costs = sum(
            1
            for recipe in self.recipes
            for ingredient_name in recipe.ingredients.keys()
            if ingredient_name not in self.ingredient_costs
        )

        if num_missing_costs > 0:
            print(
                f"Warning: {num_missing_costs} ingredient(s) used in the recipes do not have a cost defined in the meal planning environment. Defaulting to 1.0 €/100g for missing ingredients."
            )
