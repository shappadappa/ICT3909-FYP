"""
mock_data.py — Static mock data for the GA Meal Planner POC.

Provides a pantry stocked with 15 ingredients at varied expiry dates (some
urgently expiring) as well as 15 recipes that draw on those ingredients.
The current simulation date is 2026-03-19.
"""

from datetime import datetime

from models import DietaryTag, Ingredient, NutritionalInformation, Pantry, Recipe, UserPreferences

# Reference date for the simulation
CURRENT_DATE = datetime(2026, 3, 19)

# Cost (EUR) to purchase one unit of an ingredient if not in the pantry
INGREDIENT_UNIT_COSTS: dict[str, float] = {
    "tomato":         0.40,
    "pasta":          0.30,
    "chicken_breast": 2.50,
    "eggs":           0.25,
    "milk":           0.20,
    "cheese":         0.60,
    "onion":          0.30,
    "garlic":         0.15,
    "spinach":        0.80,
    "bread":          0.20,
    "butter":         0.40,
    "olive_oil":      0.50,
    "lemon":          0.30,
    "bell_pepper":    0.70,
    "mushrooms":      0.90,
}


def create_mock_pantry() -> Pantry:
    """Return a Pantry pre-loaded with 15 mock ingredients.

    Expiry urgency summary (relative to 2026-03-19):
        1 day  — spinach
        2 days — tomato, mushrooms
        3 days — chicken_breast
        4 days — bread, bell_pepper
        5 days — milk
        7 days — lemon
       10 days — eggs
       14 days — cheese
       20 days — onion
       21 days — butter
       30 days — pasta, garlic
       60 days — olive_oil
    """
    pantry = Pantry()

    ingredients = [
        Ingredient(
            name="tomato",
            quantity=4,
            nutritional_info=NutritionalInformation(22, 4.8, 3.2, 1.1, 0.2, 0.03, 1.5, 6,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 21),   # 2 days
            estimated_financial_cost=0.40,
        ),
        Ingredient(
            name="pasta",
            quantity=5,
            nutritional_info=NutritionalInformation(131, 25.0, 0.5, 5.0, 1.1, 0.2, 1.8, 1,
                                                    False, True, True, True),
            estimated_expiration_date=datetime(2026, 4, 18),   # 30 days
            estimated_financial_cost=0.30,
        ),
        Ingredient(
            name="chicken_breast",
            quantity=2,
            nutritional_info=NutritionalInformation(165, 0, 0, 31, 3.6, 1.0, 0, 74,
                                                    True, True, False, False),
            estimated_expiration_date=datetime(2026, 3, 22),   # 3 days
            estimated_financial_cost=2.50,
        ),
        Ingredient(
            name="eggs",
            quantity=6,
            nutritional_info=NutritionalInformation(155, 1.1, 1.1, 13, 11, 3.3, 0, 124,
                                                    True, True, True, False),
            estimated_expiration_date=datetime(2026, 3, 29),   # 10 days
            estimated_financial_cost=0.25,
        ),
        Ingredient(
            name="milk",
            quantity=4,
            nutritional_info=NutritionalInformation(42, 5.0, 5.0, 3.4, 1.0, 0.6, 0, 44,
                                                    True, False, True, False),
            estimated_expiration_date=datetime(2026, 3, 24),   # 5 days
            estimated_financial_cost=0.20,
        ),
        Ingredient(
            name="cheese",
            quantity=3,
            nutritional_info=NutritionalInformation(402, 1.3, 0.5, 25, 33, 21, 0, 621,
                                                    True, False, True, False),
            estimated_expiration_date=datetime(2026, 4, 2),    # 14 days
            estimated_financial_cost=0.60,
        ),
        Ingredient(
            name="onion",
            quantity=3,
            nutritional_info=NutritionalInformation(40, 9.3, 4.2, 1.1, 0.1, 0.04, 1.7, 4,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 4, 8),    # 20 days
            estimated_financial_cost=0.30,
        ),
        Ingredient(
            name="garlic",
            quantity=4,
            nutritional_info=NutritionalInformation(149, 33, 1.0, 6.4, 0.5, 0.1, 2.1, 17,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 4, 18),   # 30 days
            estimated_financial_cost=0.15,
        ),
        Ingredient(
            name="spinach",
            quantity=2,
            nutritional_info=NutritionalInformation(23, 3.6, 0.4, 2.9, 0.4, 0.1, 2.2, 79,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 20),   # 1 day ← urgent
            estimated_financial_cost=0.80,
        ),
        Ingredient(
            name="bread",
            quantity=4,
            nutritional_info=NutritionalInformation(265, 49, 5.0, 9.0, 3.2, 0.7, 2.7, 491,
                                                    False, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 23),   # 4 days
            estimated_financial_cost=0.20,
        ),
        Ingredient(
            name="butter",
            quantity=3,
            nutritional_info=NutritionalInformation(717, 0.1, 0.1, 0.9, 81, 51, 0, 11,
                                                    True, False, True, False),
            estimated_expiration_date=datetime(2026, 4, 9),    # 21 days
            estimated_financial_cost=0.40,
        ),
        Ingredient(
            name="olive_oil",
            quantity=5,
            nutritional_info=NutritionalInformation(884, 0, 0, 0, 100, 14, 0, 2,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 5, 18),   # 60 days
            estimated_financial_cost=0.50,
        ),
        Ingredient(
            name="lemon",
            quantity=2,
            nutritional_info=NutritionalInformation(29, 9.3, 2.5, 1.1, 0.3, 0.04, 2.8, 2,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 26),   # 7 days
            estimated_financial_cost=0.30,
        ),
        Ingredient(
            name="bell_pepper",
            quantity=2,
            nutritional_info=NutritionalInformation(31, 6.0, 4.2, 1.0, 0.3, 0.05, 2.1, 4,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 23),   # 4 days
            estimated_financial_cost=0.70,
        ),
        Ingredient(
            name="mushrooms",
            quantity=2,
            nutritional_info=NutritionalInformation(22, 3.3, 2.0, 3.1, 0.3, 0.05, 1.0, 5,
                                                    True, True, True, True),
            estimated_expiration_date=datetime(2026, 3, 21),   # 2 days ← urgent
            estimated_financial_cost=0.90,
        ),
    ]

    for ing in ingredients:
        pantry.add(ing)

    return pantry


def create_mock_recipes() -> list[Recipe]:
    """Return 15 recipes that draw on the mock pantry ingredients."""
    return [
        Recipe(
            name="Pasta Arrabbiata",
            ingredients={"tomato": 2, "pasta": 2, "garlic": 1, "olive_oil": 1},
            nutritional_info=NutritionalInformation(380, 65, 8, 13, 8, 1.2, 4, 15,
                                                    False, True, True, True),
            dietary_tags = [DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE]
        ),
        Recipe(
            name="Chicken Stir-Fry",
            ingredients={"chicken_breast": 1, "bell_pepper": 1, "onion": 1,
                         "garlic": 1, "olive_oil": 1},
            nutritional_info=NutritionalInformation(320, 12, 6, 35, 15, 3, 3, 450,
                                                    True, True, False, False),
            dietary_tags = [DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Spinach Omelette",
            ingredients={"spinach": 1, "eggs": 3, "butter": 1},
            nutritional_info=NutritionalInformation(280, 5, 2, 20, 21, 8, 2, 300,
                                                    True, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Mushroom Toast",
            ingredients={"mushrooms": 1, "bread": 2, "butter": 1},
            nutritional_info=NutritionalInformation(320, 40, 6, 10, 14, 6, 4, 520,
                                                    False, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Greek Salad",
            ingredients={"tomato": 2, "lemon": 1, "olive_oil": 1},
            nutritional_info=NutritionalInformation(180, 15, 8, 3, 12, 2, 3, 200,
                                                    True, True, True, True),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Chicken Pasta",
            ingredients={"chicken_breast": 1, "pasta": 2, "onion": 1,
                         "garlic": 1, "olive_oil": 1},
            nutritional_info=NutritionalInformation(450, 55, 4, 38, 10, 2, 3, 380,
                                                    False, True, False, True),
            dietary_tags=[DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Scrambled Eggs",
            ingredients={"eggs": 3, "butter": 1, "milk": 1},
            nutritional_info=NutritionalInformation(300, 4, 3, 18, 24, 10, 0, 350,
                                                    True, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Tomato Soup",
            ingredients={"tomato": 3, "onion": 1, "garlic": 1, "olive_oil": 1},
            nutritional_info=NutritionalInformation(150, 18, 10, 4, 7, 1, 4, 320,
                                                    True, True, True, True),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Cheese Toast",
            ingredients={"bread": 2, "cheese": 1, "butter": 1},
            nutritional_info=NutritionalInformation(420, 42, 4, 16, 22, 12, 2, 680,
                                                    False, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Bell Pepper Frittata",
            ingredients={"bell_pepper": 1, "eggs": 4, "onion": 1, "cheese": 1},
            nutritional_info=NutritionalInformation(350, 10, 6, 24, 25, 10, 3, 490,
                                                    True, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE],
        ),
        Recipe(
            name="Pasta with Mushrooms",
            ingredients={"pasta": 2, "mushrooms": 1, "garlic": 1,
                         "olive_oil": 1, "cheese": 1},
            nutritional_info=NutritionalInformation(410, 60, 5, 16, 14, 5, 4, 380,
                                                    False, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Chicken Omelette",
            ingredients={"chicken_breast": 1, "eggs": 2, "spinach": 1},
            nutritional_info=NutritionalInformation(360, 4, 1, 45, 19, 5, 2, 420,
                                                    True, True, False, True),
            dietary_tags=[DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="French Toast",
            ingredients={"bread": 2, "eggs": 2, "milk": 1, "butter": 1},
            nutritional_info=NutritionalInformation(380, 48, 8, 15, 17, 7, 2, 580,
                                                    False, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
        Recipe(
            name="Stuffed Peppers",
            ingredients={"bell_pepper": 2, "tomato": 1, "onion": 1, "garlic": 1},
            nutritional_info=NutritionalInformation(200, 25, 12, 7, 8, 1.5, 5, 280,
                                                    True, True, True, True),
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE, DietaryTag.LACTOSE_FREE],
        ),
        Recipe(
            name="Creamy Pasta",
            ingredients={"pasta": 2, "cheese": 2, "butter": 1, "milk": 1},
            nutritional_info=NutritionalInformation(550, 62, 6, 20, 28, 17, 3, 720,
                                                    False, False, True, False),
            dietary_tags=[DietaryTag.VEGETARIAN],
        ),
    ]


def create_default_preferences() -> UserPreferences:
    """Return default user preferences (no dietary restrictions, EUR 50/week budget)."""
    return UserPreferences(
        weekly_budget=50.0,
        calorie_target_per_day=2500.0,
        is_vegetarian=False,
        is_vegan=False,
        requires_gluten_free=False,
        requires_lactose_free=False,
    )
