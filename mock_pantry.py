"""
mock_data.py — Static mock data for the GA Meal Planner POC.

Provides a pantry stocked with 15 ingredients at varied expiry dates (some
urgently expiring) as well as 15 recipes that draw on those ingredients.
The current simulation date is 2026-03-19.
"""

from datetime import datetime, timedelta
from random import randint, seed

from models import DietaryTag, Ingredient, NutritionalInformation, Pantry, Recipe, UserPreferences

CURRENT_DATE = datetime.now()

def get_date(days_from_now: int) -> datetime:
    return CURRENT_DATE + timedelta(days=days_from_now)

# cost (EUR) to purchase one unit of an ingredient
INGREDIENT_UNIT_COSTS: dict[str, float] = {
    "tomato": 0.40,
    "pasta": 0.30,
    "chicken_breast": 2.50,
    "eggs": 0.25,
    "milk": 0.20,
    "cheese": 0.60,
    "onion": 0.30,
    "garlic": 0.15,
    "spinach": 0.80,
    "bread": 0.20,
    "butter": 0.40,
    "olive_oil": 0.50,
    "lemon": 0.30,
    "bell_pepper": 0.70,
    "mushrooms": 0.90,
}

# Catalog of ingredient definitions: name -> (grams_per_unit, NutritionalInformation)
# Nutritional values are per 100 g; grams_per_unit is the weight of one standard unit
_INGREDIENT_DEFINITIONS: dict[str, tuple[float, NutritionalInformation]] = {
    "tomato": (150.0, NutritionalInformation(22, 4.8, 3.2, 1.1, 0.2, 0.03, 1.5, 6, True, True, True, True)),
    "pasta": (80.0, NutritionalInformation(131, 25.0, 0.5, 5.0, 1.1, 0.20, 1.8, 1, False, True, True, True)),
    "chicken_breast": (200.0, NutritionalInformation(165, 0.0, 0.0, 31.0,  3.6,  1.00, 0.0, 74, True, True, False, False)),
    "eggs": (60.0, NutritionalInformation(155, 1.1, 1.1, 13.0, 11.0,  3.30, 0.0, 124, True,  True,  True,  False)),
    "milk": (240.0, NutritionalInformation( 42, 5.0, 5.0,  3.4,  1.0,  0.60, 0.0,  44, True,  False, True,  False)),
    "cheese": (30.0, NutritionalInformation(402, 1.3, 0.5, 25.0, 33.0, 21.00, 0.0, 621, True,  False, True,  False)),
    "onion": (150.0, NutritionalInformation(40, 9.3, 4.2, 1.1, 0.1, 0.04, 1.7, 4, True,  True,  True,  True)),
    "garlic": (5.0, NutritionalInformation(149, 33.0, 1.0, 6.4, 0.5, 0.10, 2.1, 17, True,  True,  True, True)),
    "spinach": (30.0, NutritionalInformation(23, 3.6, 0.4, 2.9, 0.4, 0.10, 2.2, 79, True,  True,  True, True)),
    "bread": (28.0, NutritionalInformation(265, 49.0, 5.0, 9.0, 3.2, 0.70, 2.7, 491, False, True,  True, True)),
    "butter": (14.0, NutritionalInformation(717, 0.1, 0.1, 0.9, 81.0, 51.00, 0.0, 11, True,  False, True, False)),
    "olive_oil": (14.0, NutritionalInformation(884, 0.0, 0.0, 0.0,100.0, 14.00, 0.0, 2, True,  True, True, True)),
    "lemon": (100.0, NutritionalInformation(29, 9.3, 2.5, 1.1, 0.3, 0.04, 2.8, 2, True,  True, True, True)),
    "bell_pepper": (120.0, NutritionalInformation(31, 6.0, 4.2, 1.0, 0.3, 0.05, 2.1, 4, True, True, True, True)),
    "mushrooms": (70.0, NutritionalInformation(22, 3.3, 2.0, 3.1, 0.3, 0.05, 1.0, 5, True, True, True, True)),
}

_INGREDIENT_NAMES = list(_INGREDIENT_DEFINITIONS.keys())

def make_ingredient(name: str, expiration_date: datetime | None = None) -> Ingredient:
    """
    Creates an Ingredient for the given name using the shared catalog data.
    Pass an expiration_date when creating a pantry item; omit it for recipe ingredient references.

    :param name: ingredient name (must exist in the catalog)
    :type name: str
    :param expiration_date: expiry date for pantry use (default = datetime(9999, 12, 31), meaning it does not expire)
    :type expiration_date: datetime
    :return: Ingredient instance
    :rtype: Ingredient
    """

    grams_per_unit, nutritional_info = _INGREDIENT_DEFINITIONS [name]

    return Ingredient(
        name = name,
        grams_per_unit = grams_per_unit,
        nutritional_info = nutritional_info,
        estimated_expiration_date = expiration_date if expiration_date is not None else datetime(9999, 12, 31),
        estimated_financial_cost = INGREDIENT_UNIT_COSTS[name],
    )

def create_mock_pantry(num_ingredients: int, random_state: int | None = None) -> Pantry:
    """
    Create a mock pantry with a specified number of ingredients at varied expiry dates (some urgently expiring)

    :param num_ingredients: number of ingredients to include in the pantry
    :type num_ingredients: int

    :param random_state: optional random seed for reproducibility
    :type random_state: int | None

    :return: Pantry object representing the mock pantry
    :rtype: Pantry
    """

    if random_state is not None:
        seed(random_state)

    pantry = Pantry()

    for _ in range(num_ingredients):
        name = _INGREDIENT_NAMES[randint(0, 14)]
        ingredient = make_ingredient(name, get_date(randint(0, 30)))
        pantry.add(ingredient, 1)

    return pantry


def create_mock_recipes() -> list[Recipe]:
    """
    15 mock recipes

    :return: list of Recipe objects representing the mock recipes
    :rtype: list[Recipe]
    """
   
    def ing(name: str) -> Ingredient:
        return make_ingredient(name)

    return [
        Recipe(
            name="Pasta Arrabbiata",
            ingredients={ing("tomato"): 2, ing("pasta"): 2, ing("garlic"): 1, ing("olive_oil"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Chicken Stir-Fry",
            ingredients={ing("chicken_breast"): 1, ing("bell_pepper"): 1, ing("onion"): 1,
                         ing("garlic"): 1, ing("olive_oil"): 1},
            dietary_tags=[DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Spinach Omelette",
            ingredients={ing("spinach"): 1, ing("eggs"): 3, ing("butter"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Mushroom Toast",
            ingredients={ing("mushrooms"): 1, ing("bread"): 2, ing("butter"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Greek Salad",
            ingredients={ing("tomato"): 2, ing("lemon"): 1, ing("olive_oil"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Chicken Pasta",
            ingredients={ing("chicken_breast"): 1, ing("pasta"): 2, ing("onion"): 1,
                         ing("garlic"): 1, ing("olive_oil"): 1},
            dietary_tags=[DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Scrambled Eggs",
            ingredients={ing("eggs"): 3, ing("butter"): 1, ing("milk"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Tomato Soup",
            ingredients={ing("tomato"): 3, ing("onion"): 1, ing("garlic"): 1, ing("olive_oil"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Cheese Toast",
            ingredients={ing("bread"): 2, ing("cheese"): 1, ing("butter"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Bell Pepper Frittata",
            ingredients={ing("bell_pepper"): 1, ing("eggs"): 4, ing("onion"): 1, ing("cheese"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Pasta with Mushrooms",
            ingredients={ing("pasta"): 2, ing("mushrooms"): 1, ing("garlic"): 1,
                         ing("olive_oil"): 1, ing("cheese"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Chicken Omelette",
            ingredients={ing("chicken_breast"): 1, ing("eggs"): 2, ing("spinach"): 1},
            dietary_tags=[DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="French Toast",
            ingredients={ing("bread"): 2, ing("eggs"): 2, ing("milk"): 1, ing("butter"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Stuffed Peppers",
            ingredients={ing("bell_pepper"): 2, ing("tomato"): 1, ing("onion"): 1, ing("garlic"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Creamy Pasta",
            ingredients={ing("pasta"): 2, ing("cheese"): 2, ing("butter"): 1, ing("milk"): 1},
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
    ]


def create_default_preferences() -> UserPreferences:
    """
    Create default user preferences for the meal planner

    :return: UserPreferences object representing the default preferences
    :rtype: UserPreferences
    """

    return UserPreferences(
        weekly_budget=50.0,
        calorie_target_per_day=2500.0,
        protein_target_per_day=50.0,
        is_vegetarian=False,
        is_vegan=False,
        requires_gluten_free=True,
        requires_lactose_free=False,
    )


if __name__ == "__main__":
    pantry = create_mock_pantry(num_ingredients=10, random_state=42)
    print("=== Mock Pantry Contents ===")
    pantry.print()