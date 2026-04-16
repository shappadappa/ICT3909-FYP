from models.DietaryTag import DietaryTag
from models.Ingredient import Ingredient
from models.NutritionalInformation import NutritionalInformation


class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict[str, int],
        dietary_tags: list[DietaryTag],
        instructions: list[str] = [],
    ):
        """
        The `Recipe` class represents a recipe with its required ingredients and dietary properties.
        Nutritional information is computed separately by calling `compute_nutritional_information`.

        :param name: display name of the recipe
        :type name: str
        :param ingredients: mapping of ingredient names to number of grams required for the recipe
        :type ingredients: dict[strs, int]
        :param dietary_tags: list of dietary compliance tags
        :type dietary_tags: list[DietaryTag]
        :param instructions: list of step-by-step instructions for preparing the recipe (optional)
        :type instructions: list[str]
        """

        self.name = name
        self.ingredients = ingredients
        self.dietary_tags = dietary_tags
        self.instructions = instructions

        self.is_vegan = DietaryTag.VEGAN in dietary_tags
        self.is_vegetarian = DietaryTag.VEGETARIAN in dietary_tags or self.is_vegan
        self.is_gluten_free = DietaryTag.GLUTEN_FREE in dietary_tags
        self.is_lactose_free = DietaryTag.LACTOSE_FREE in dietary_tags

        self.nutritional_information = NutritionalInformation()

    def compute_nutritional_information(self, ingredient_lookup: dict[str, Ingredient]) -> NutritionalInformation:
        """
        Sums the per-unit nutritional values of all ingredients, scaled by their quantities, to produce the total nutritional information for the recipe

        :param ingredient_lookup: mapping of ingredient names to Ingredient objects
        :type ingredient_lookup: dict[str, Ingredient]

        :return: total nutritional information for the recipe
        :rtype: NutritionalInformation
        """

        self.nutritional_information = NutritionalInformation()

        for ingredient_name, quantity in self.ingredients.items():
            ingredient = ingredient_lookup.get(ingredient_name)

            if not ingredient:
                continue

            scale = quantity / 100.0

            for nutritional_attribute in ingredient.nutritional_information.keys:
                # bool attributes: is_gluten_free, is_lactose_free, is_vegetarian, is_vegan. Only changed if False or None, since when True, the recipe is only as compliant as its least compliant ingredient
                if isinstance(
                    ingredient.nutritional_information.get_nutritional_value(nutritional_attribute),
                    bool,
                ) and ingredient.nutritional_information.get_nutritional_value(nutritional_attribute) in [False, None]:
                    self.nutritional_information.set_nutritional_value(
                        nutritional_attribute,
                        ingredient.nutritional_information.get_nutritional_value(nutritional_attribute),  # type: ignore
                    )
                # float attributes: calories, carbohydrates, sugar, protein, fat, saturated_fat, fiber, sodium
                elif not isinstance(
                    ingredient.nutritional_information.get_nutritional_value(nutritional_attribute),
                    bool,
                ) and isinstance(
                    ingredient.nutritional_information.get_nutritional_value(nutritional_attribute),
                    (int, float),
                ):
                    per_100g_value = ingredient.nutritional_information.get_nutritional_value(nutritional_attribute)

                    if per_100g_value is not None:
                        old_value = self.nutritional_information.get_nutritional_value(nutritional_attribute) or 0.0
                        new_value = old_value + (per_100g_value * scale)
                        self.nutritional_information.set_nutritional_value(nutritional_attribute, new_value)
                    continue

        # default any unset bool attributes to True since no ingredient flagged non-compliance
        for nutritional_attribute in self.nutritional_information.keys:
            value = self.nutritional_information.get_nutritional_value(nutritional_attribute)

            if value is None:
                sample = next(
                    (
                        i.nutritional_information.get_nutritional_value(nutritional_attribute)
                        for i in ingredient_lookup.values()
                        if isinstance(
                            i.nutritional_information.get_nutritional_value(nutritional_attribute),
                            bool,
                        )
                    ),
                    None,
                )

                if sample is not None:
                    self.nutritional_information.set_nutritional_value(nutritional_attribute, True)

        return self.nutritional_information

    def print(self):
        """
        Prints a summary of the recipe's details
        """

        instructions_text = "\n".join(self.instructions)

        print(
            f"Recipe Title: {self.name}\n"
            f"Ingredients: {', '.join(list(self.ingredients.keys()))}\n"
            f"Dietary Tags: {', '.join([tag.name for tag in self.dietary_tags])}\n"
            f"Instructions:\n{instructions_text}\n"
            f"\tNutritional Information:"
        )

        self.nutritional_information.print(2)

    def to_dict(self):
        """
        Converts the recipe object to a dictionary format
        """

        return {
            "name": self.name,
            "ingredients": [
                {"ingredient": ingredient_name, "quantity": quantity}
                for ingredient_name, quantity in self.ingredients.items()
            ],
            "dietary_tags": [tag.name for tag in self.dietary_tags],
            "instructions": self.instructions,
            "nutritional_information": self.nutritional_information.to_dict(),
        }
