from models.DietaryTag import DietaryTag
from models.NutritionalInformation import NutritionalInformation
from models.Ingredient import Ingredient

class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict[Ingredient, int],
        dietary_tags: list[DietaryTag],
        instructions: list[str] = [],
        serves: int = 1
    ):
        """
        The `Recipe` class represents a recipe with its required ingredients and dietary properties.
        Nutritional information is automatically derived from the ingredient list.

        :param name: display name of the recipe
        :type name: str
        :param ingredients: mapping of Ingredient to number of grams required for the recipe
        :type ingredients: dict[Ingredient, int]
        :param dietary_tags: list of dietary compliance tags
        :type dietary_tags: list[DietaryTag]
        :param instructions: list of step-by-step instructions for preparing the recipe (optional)
        :type instructions: list[str]
        :param serves: number of servings the recipe makes (default = 1)
        :type serves: int
        """

        self.name = name
        self.ingredients = ingredients
        self.dietary_tags = dietary_tags
        self.instructions = instructions
        self.serves = serves
        
        self.is_vegan = DietaryTag.VEGAN in dietary_tags
        self.is_vegetarian = DietaryTag.VEGETARIAN in dietary_tags or self.is_vegan
        self.is_gluten_free = DietaryTag.GLUTEN_FREE in dietary_tags
        self.is_lactose_free = DietaryTag.LACTOSE_FREE in dietary_tags

        self.nutritional_information = self._compute_nutritional_information()

    def _compute_nutritional_information(self) -> NutritionalInformation:
        """
        Sums the per-unit nutritional values of all ingredients, scaled by their quantities, to produce the total nutritional information for the recipe

        :return: total nutritional information for the recipe
        :rtype: NutritionalInformation
        """

        # ! This nutritional information is for all servings of the recipe. To get per-serving nutritional information, divide the returned values by self.serves

        recipe_nutritional_information = NutritionalInformation()

        for ingredient, quantity in self.ingredients.items():
            scale = quantity / 100.0

            for nutritional_attribute in ingredient.nutritional_information.keys:
                # float attributes: calories, carbohydrates, sugar, protein, fat, saturated_fat, fiber, sodium
                if isinstance(ingredient.nutritional_information.get_nutritional_value(nutritional_attribute), (int, float)):
                    per_100g_value = ingredient.nutritional_information.get_nutritional_value(nutritional_attribute)

                    if per_100g_value is not None:
                        old_value = recipe_nutritional_information.get_nutritional_value(nutritional_attribute) or 0.0
                        new_value = old_value + (per_100g_value * scale)
                        recipe_nutritional_information.set_nutritional_value(nutritional_attribute, new_value)
                    continue
            
                # bool attributes: is_gluten_free, is_lactose_free, is_vegetarian, is_vegan. Only changed if False or None, since when True, the recipe is only as compliant as its least compliant ingredient
                if isinstance(ingredient.nutritional_information.get_nutritional_value(nutritional_attribute), bool) and ingredient.nutritional_information.get_nutritional_value(nutritional_attribute) in [False, None]:
                    recipe_nutritional_information.set_nutritional_value(nutritional_attribute, ingredient.nutritional_information.get_nutritional_value(nutritional_attribute))

        return recipe_nutritional_information

    @property
    def ingredient_quantities(self) -> dict[str, int]:
        """
        Returns ingredient name to unit quantity mapping for use in pantry-lookup code

        :return: mapping of ingredient name to number of units required
        :rtype: dict[str, int]
        """

        return {ingredient.name: quantity for ingredient, quantity in self.ingredients.items()}

    def print(self):
        """
        Prints a summary of the recipe's details
        """

        instructions_text = "\n".join(self.instructions)

        print(
            f"Recipe Title: {self.name}\n"
            f"Ingredients: {', '.join([ingredient.name for ingredient in self.ingredients])}\n"
            f"Dietary Tags: {', '.join([tag.name for tag in self.dietary_tags])}\n"
            f"Instructions:\n{instructions_text}\n"
            f"Serves: {self.serves}\n"
            f"\tNutritional Information:"
        )

        self.nutritional_information.print(2)