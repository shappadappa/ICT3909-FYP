import json
from datetime import datetime, timedelta

from models import NutritionalInformation, Pantry, PantryIngredient, Recipe, UserPreferences
from models.DietaryTag import DietaryTag
from models.Ingredient import Ingredient


def load_all_ingredients(filepath: str) -> list[Ingredient]:
    """
    Loads all ingredients from a structured JSON file

    :param filepath: path to the JSON file containing ingredient data
    :type filepath: str

    :return: list of Ingredient objects
    :rtype: list[Ingredient]
    """

    ingredients = []

    with open(filepath, "r", encoding="utf-8") as f:
        ingredients_data = json.load(f)

    for ingredient_data in ingredients_data:
        nutritional_information = NutritionalInformation(**ingredient_data["nutritional_information"])
        ingredient = Ingredient(name=ingredient_data["name"], nutritional_information=nutritional_information)
        ingredients.append(ingredient)

    return ingredients


def get_ingredient(ingredient_name: str, all_ingredients: list[Ingredient]) -> Ingredient | None:
    """
    Finds an ingredient by name from a list of ingredients

    :param ingredient_name: the name of the ingredient to find
    :type ingredient_name: str
    :param all_ingredients: list of available Ingredient objects to search
    :type all_ingredients: list[Ingredient]

    :return: the matching Ingredient, or None if not found
    :rtype: Ingredient | None
    """

    return next((ingredient for ingredient in all_ingredients if ingredient.name == ingredient_name), None)


def get_pantry_ingredient(
    ingredient_name: str,
    estimated_expiration_date: datetime,
    estimated_financial_cost: float,
    all_ingredients: list[Ingredient],
) -> PantryIngredient:
    """
    Creates a PantryIngredient from a named ingredient in a known ingredient list

    :param ingredient_name: name of the ingredient to look up
    :type ingredient_name: str
    :param estimated_expiration_date: estimated expiry date for the pantry item
    :type estimated_expiration_date: datetime
    :param estimated_financial_cost: estimated cost per unit in EUR
    :type estimated_financial_cost: float
    :param all_ingredients: list of available Ingredient objects to search
    :type all_ingredients: list[Ingredient]

    :return: a PantryIngredient built from the matching Ingredient
    :rtype: PantryIngredient

    :raises ValueError: if the ingredient name is not found in all_ingredients
    """

    ingredient = get_ingredient(ingredient_name, all_ingredients)

    if ingredient is None:
        raise ValueError(f"Ingredient '{ingredient_name}' not found in ingredient list")

    return PantryIngredient(
        name=ingredient.name,
        nutritional_information=ingredient.nutritional_information,
        estimated_expiration_date=estimated_expiration_date,
        estimated_financial_cost=estimated_financial_cost,
    )


def make_recipe(
    name: str,
    ingredients: dict[str, float],
    calories: float = 0.0,
    protein: float = 0.0,
    tags: list[DietaryTag] | None = None,
) -> Recipe:
    """
    Builds a Recipe with the given nutritional values and dietary tags. Nutritional information is set directly rather than computed from ingredients when using this function

    :param name: display name of the recipe
    :type name: str
    :param ingredients: mapping of ingredient names to quantities in grams
    :type ingredients: dict[str, float]
    :param calories: total calories for the recipe in kcal
    :type calories: float
    :param protein: total protein for the recipe in grams
    :type protein: float
    :param tags: list of dietary tags
    :type tags: list[DietaryTag] | None

    :return: a Recipe with pre-set nutritional information
    :rtype: Recipe
    """

    recipe = Recipe(name=name, ingredients=ingredients, dietary_tags=tags or [])
    recipe.nutritional_information = NutritionalInformation(calories=calories, protein=protein)
    return recipe


def make_pantry(items: dict[str, tuple[float, int]]) -> Pantry:
    """
    Builds a Pantry from a plain dictionary. Ingredients are created with empty nutritional information, which is useful for testing metric calculations

    :param items: mapping of ingredient name to (quantity_in_grams, days_until_expiry)
    :type items: dict[str, tuple[float, int]]

    :return: a populated Pantry object
    :rtype: Pantry
    """

    pantry = Pantry()
    now = datetime.now()

    for name, (quantity, days) in items.items():
        pantry_ingredient = PantryIngredient(
            name=name,
            nutritional_information=NutritionalInformation(),
            estimated_expiration_date=now + timedelta(days=days),
        )
        pantry.add(pantry_ingredient, quantity)

    return pantry


def make_preferences(
    calorie_target: float = 2000.0,
    protein_target: float = 50.0,
    weekly_budget: float = 50.0,
    is_vegetarian: bool = False,
    is_vegan: bool = False,
    requires_gluten_free: bool = False,
    requires_lactose_free: bool = False,
) -> UserPreferences:
    """
    Builds a UserPreferences object with the given targets and restrictions

    :param calorie_target: daily calorie target in kcal
    :type calorie_target: float
    :param protein_target: daily protein target in grams
    :type protein_target: float
    :param weekly_budget: weekly grocery budget in EUR
    :type weekly_budget: float
    :param is_vegetarian: whether the user requires vegetarian meals
    :type is_vegetarian: bool
    :param is_vegan: whether the user requires vegan meals
    :type is_vegan: bool
    :param requires_gluten_free: whether the user requires gluten-free meals
    :type requires_gluten_free: bool
    :param requires_lactose_free: whether the user requires lactose-free meals
    :type requires_lactose_free: bool

    :return: a UserPreferences object
    :rtype: UserPreferences
    """

    return UserPreferences(
        weekly_budget=weekly_budget,
        calorie_target_per_day=calorie_target,
        protein_target_per_day=protein_target,
        is_vegetarian=is_vegetarian,
        is_vegan=is_vegan,
        requires_gluten_free=requires_gluten_free,
        requires_lactose_free=requires_lactose_free,
    )
