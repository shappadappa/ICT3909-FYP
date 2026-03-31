from models.DietaryTag import DietaryTag
from models.NutritionalInformation import NutritionalInformation
from models.Ingredient import Ingredient

class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict[Ingredient, int],
        dietary_tags: list[DietaryTag],
    ):
        """
        The `Recipe` class represents a recipe with its required ingredients and dietary properties.
        Nutritional information is automatically derived from the ingredient list.

        :param name: display name of the recipe
        :type name: str
        :param ingredients: mapping of Ingredient to number of units required
        :type ingredients: dict[Ingredient, int]
        :param dietary_tags: list of dietary compliance tags
        :type dietary_tags: list[DietaryTag]
        """

        self.name = name
        self.ingredients = ingredients
        self.dietary_tags = dietary_tags

        self.is_vegan = DietaryTag.VEGAN in dietary_tags
        self.is_vegetarian = DietaryTag.VEGETARIAN in dietary_tags or self.is_vegan
        self.is_gluten_free = DietaryTag.GLUTEN_FREE in dietary_tags
        self.is_lactose_free = DietaryTag.LACTOSE_FREE in dietary_tags

        self.nutritional_info = self._compute_nutritional_info()

    def _compute_nutritional_info(self) -> NutritionalInformation:
        """
        Sums the per-unit nutritional values of all ingredients, scaled by their quantities, to produce the total nutritional information for the recipe

        :return: total nutritional information for the recipe
        :rtype: NutritionalInformation
        """

        calories = carbohydrates = sugar = protein = 0.0
        fat = saturated_fat = fiber = sodium = 0.0

        for ingredient, quantity in self.ingredients.items():
            per_unit = ingredient.nutrition_per_unit()
            calories += per_unit.calories * quantity
            carbohydrates += per_unit.carbohydrates * quantity
            sugar += per_unit.sugar * quantity
            protein += per_unit.protein * quantity
            fat += per_unit.fat * quantity
            saturated_fat += per_unit.saturated_fat * quantity
            fiber += per_unit.fiber * quantity
            sodium += per_unit.sodium * quantity

        is_gluten_free = all(ing.nutritional_info.is_gluten_free for ing in self.ingredients)
        is_lactose_free = all(ing.nutritional_info.is_lactose_free for ing in self.ingredients)
        is_vegetarian = all(ing.nutritional_info.is_vegetarian for ing in self.ingredients)
        is_vegan = all(ing.nutritional_info.is_vegan for ing in self.ingredients)

        return NutritionalInformation(calories, carbohydrates, sugar, protein, fat, saturated_fat, fiber, sodium, is_gluten_free, is_lactose_free, is_vegetarian, is_vegan)

    @property
    def ingredient_quantities(self) -> dict[str, int]:
        """
        Returns ingredient name to unit quantity mapping for use in pantry-lookup code

        :return: mapping of ingredient name to number of units required
        :rtype: dict[str, int]
        """

        return {ingredient.name: quantity for ingredient, quantity in self.ingredients.items()}
