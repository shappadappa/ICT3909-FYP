from models import Ingredient, NutritionalInformation, Pantry

from datetime import datetime

print("Pantry Management System:")

pantry = Pantry()

ingredient_1 = Ingredient(
    name = "tomato",
    quantity = 2,
    nutritional_info = NutritionalInformation(
        calories = 22,
        carbohydrates = 4.8,
        sugar = 3.2,
        protein = 1.1,
        fat = 0.2,
        saturated_fat = 0.03,
        fiber = 1.5,
        sodium = 6,
        is_gluten_free = True,
        is_lactose_free = True,
        is_vegetarian = True,
        is_vegan = True
    ),
    estimated_expiration_date = datetime.strptime("20-03-2027", "%d-%m-%Y"),
    estimated_financial_cost = 0.50
)

pantry.add(ingredient_1)
pantry.print()