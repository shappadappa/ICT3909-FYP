import json
from datetime import datetime, timedelta
from random import sample, seed

from models import NutritionalInformation, Pantry, PantryIngredient, Recipe, UserPreferences
from models.DietaryTag import DietaryTag
from models.Ingredient import Ingredient


def load_all_ingredients(filepath: str) -> list[Ingredient]:
    """
    Loads all ingredients from a structured JSON file.

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
    Finds an ingredient by name from a list of ingredients.

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
    all_ingredients: list[Ingredient],
) -> PantryIngredient:
    """
    Creates a PantryIngredient from a named ingredient in a known ingredient list.

    :param ingredient_name: name of the ingredient to look up
    :type ingredient_name: str
    :param estimated_expiration_date: estimated expiry date for the pantry item
    :type estimated_expiration_date: datetime
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
    )


def make_recipe(
    name: str,
    ingredients: dict[str, float],
    calories: float = 0.0,
    protein: float = 0.0,
    tags: list[DietaryTag] | None = None,
) -> Recipe:
    """
    Builds a Recipe with the given nutritional values and dietary tags. Nutritional information is set directly rather
    than computed from ingredients when using this function.

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
    Builds a Pantry from a plain dictionary. Ingredients are created with empty nutritional information, which is useful
    for testing metric calculations.

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
    Builds a UserPreferences object with the given targets and restrictions.

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


def get_consumed_stock(meal_plan: list[list[Recipe]], pantry_stock: dict[str, float]) -> dict[str, float]:
    """
    Returns a mapping of ingredient name to total quantity consumed from the pantry across a meal plan.

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry_stock: mapping of ingredient name to available quantity in grams
    :type pantry_stock: dict[str, float]
    :return: mapping of ingredient name to total quantity consumed from the pantry in grams
    :rtype: dict[str, float]
    """

    consumed_stock: dict[str, float] = dict.fromkeys(pantry_stock.keys(), 0.0)

    for day_meals in meal_plan:
        for recipe in day_meals:
            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = pantry_stock.get(ingredient_name, 0.0) - consumed_stock.get(ingredient_name, 0.0)
                from_pantry = max(0.0, min(available, quantity_needed))
                consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0.0) + from_pantry

    return consumed_stock


def filter_and_add_recipes(
    all_recipes: list[Recipe],
    pantry_ingredient_names: list[str],
    num_filtered_recipes: int,
    num_extra_recipes: int,
    user_preferences: UserPreferences = make_preferences(),
    random_seed: int | None = None,
) -> list[Recipe]:
    """
    Filters the recipe list to those that can be made with the pantry ingredients, then adds a few random extra recipes
    to increase variety.

    :param all_recipes: full list of recipes loaded from supplemented_structured_recipes.json
    :type all_recipes: list[Recipe]
    :param pantry_ingredient_names: list of ingredient names available in the pantry
    :type pantry_ingredient_names: list[str]
    :param num_filtered_recipes: maximum number of pantry-matching recipes to include
    :type num_filtered_recipes: int
    :param num_extra_recipes: number of random extra recipes to add for variety
    :type num_extra_recipes: int
    :param user_preferences: user preferences to filter recipes by dietary tags (default = no restrictions)
    :type user_preferences: UserPreferences
    :param random_seed: optional random seed for reproducibility
    :type random_seed: int | None
    :return: filtered and augmented list of recipes
    :rtype: list[Recipe]
    """

    if random_seed is not None:
        seed(random_seed)

    required_tags: set[DietaryTag] = set()

    if user_preferences.is_vegan:
        required_tags.add(DietaryTag.VEGAN)
    if user_preferences.is_vegetarian:
        required_tags.add(DietaryTag.VEGETARIAN)
    if user_preferences.requires_gluten_free:
        required_tags.add(DietaryTag.GLUTEN_FREE)
    if user_preferences.requires_lactose_free:
        required_tags.add(DietaryTag.LACTOSE_FREE)

    def satisfies_dietary_requirements(recipe: Recipe) -> bool:
        return required_tags.issubset(set(recipe.dietary_tags))

    eligible_recipes = [(i, recipe) for i, recipe in enumerate(all_recipes) if satisfies_dietary_requirements(recipe)]

    unique_ingredient_names = set(pantry_ingredient_names)

    filtered_recipe_indices = []

    for i, recipe in eligible_recipes:
        if any(ingredient_name in unique_ingredient_names for ingredient_name in recipe.ingredients.keys()):
            filtered_recipe_indices.append(i)

    if len(filtered_recipe_indices) > num_filtered_recipes:
        filtered_recipe_indices = sample(filtered_recipe_indices, num_filtered_recipes)

    eligible_recipe_indices = {i for i, _ in eligible_recipes}
    sampled_recipe_indices = sample(
        [i for i in eligible_recipe_indices if i not in filtered_recipe_indices], num_extra_recipes
    )

    assert len(set(sampled_recipe_indices).intersection(set(filtered_recipe_indices))) == 0, (
        "Sampled indices should not overlap with filtered recipe indices"
    )

    return [all_recipes[i] for i in filtered_recipe_indices + sampled_recipe_indices]


_TAG_MAP: dict[str, DietaryTag] = {
    "VEGETARIAN": DietaryTag.VEGETARIAN,
    "VEGAN": DietaryTag.VEGAN,
    "GLUTEN_FREE": DietaryTag.GLUTEN_FREE,
    "LACTOSE_FREE": DietaryTag.LACTOSE_FREE,
}


def parse_recipes(unparsed_recipes: list[dict]) -> list[Recipe]:
    """
    Parses a list of unparsed recipe dictionaries (loaded from json) into Recipe objects with nutritional information
    and dietary tags set.

    :param unparsed_recipes: list of unparsed recipe dictionaries
    :type unparsed_recipes: list[dict]
    :return: list of parsed Recipe objects
    :rtype: list[Recipe]
    """

    recipes = []

    for unparsed_recipe in unparsed_recipes:
        ingredients = {item["ingredient"]: item["quantity"] for item in unparsed_recipe["ingredients"]}
        dietary_tags = [_TAG_MAP[tag] for tag in unparsed_recipe.get("dietary_tags", []) if tag in _TAG_MAP]
        nutritional_information = unparsed_recipe.get("nutritional_information", {})

        recipe = Recipe(
            name=unparsed_recipe["name"].strip(),
            ingredients=ingredients,
            dietary_tags=dietary_tags,
            instructions=unparsed_recipe.get("instructions", []),
        )

        recipe.nutritional_information = NutritionalInformation(
            calories=nutritional_information.get("calories"),
            carbohydrates=nutritional_information.get("carbohydrates"),
            sugar=nutritional_information.get("sugar"),
            protein=nutritional_information.get("protein"),
            fat=nutritional_information.get("fat"),
            saturated_fat=nutritional_information.get("saturated_fat"),
            fiber=nutritional_information.get("fiber"),
            sodium=nutritional_information.get("sodium"),
            is_gluten_free=nutritional_information.get("is_gluten_free"),
            is_lactose_free=nutritional_information.get("is_lactose_free"),
            is_vegetarian=nutritional_information.get("is_vegetarian"),
            is_vegan=nutritional_information.get("is_vegan"),
        )

        recipes.append(recipe)

    return recipes
