import json

from models.DietaryTag import DietaryTag
from models.NutritionalInformation import NutritionalInformation
from models.Pantry import Pantry
from models.Recipe import Recipe
from models.UserPreferences import UserPreferences


class MealPlanningEnvironment:
    def __init__(
        self, recipes: list[Recipe] = [], pantry: Pantry = Pantry(), preferences: UserPreferences = UserPreferences()
    ):
        self.recipes = recipes
        self.pantry = pantry
        self.preferences = preferences

        self.ingredient_nutritional_information_lookup: dict[str, NutritionalInformation] = {}

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
            )

            recipe.nutritional_information = self._parse_nutritional_information(item["nutritional_information"])

            self.recipes.append(recipe)

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
