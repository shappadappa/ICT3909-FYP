from models.Ingredient import Ingredient

class Pantry:
    def __init__(self):
        """
        The `Pantry` class represents a collection of ingredients in the pantry
        """

        self.ingredients: list[Ingredient] = []

    def add(self, ingredient: Ingredient):
        """
        Adds an ingredient to the pantry
        
        :param ingredient: ingredient to add to the pantry
        :type ingredient: Ingredient
        """
        self.ingredients.append(ingredient)

    def print(self):
        """
        Prints the details of all ingredients in the pantry
        """

        for ingredient in self.ingredients:
            print(f"Name: {ingredient.name}")
            print(f"Quantity: {ingredient.quantity}")
            print(f"Nutritional Information: Calories: {ingredient.nutritional_info.calories}, Carbohydrates: {ingredient.nutritional_info.carbohydrates}, Sugar: {ingredient.nutritional_info.sugar}, Protein: {ingredient.nutritional_info.protein}, Fat: {ingredient.nutritional_info.fat}, Saturated Fat: {ingredient.nutritional_info.saturated_fat}, Fiber: {ingredient.nutritional_info.fiber}, Sodium: {ingredient.nutritional_info.sodium}, Gluten Free: {ingredient.nutritional_info.is_gluten_free}, Lactose Free: {ingredient.nutritional_info.is_lactose_free}, Vegetarian: {ingredient.nutritional_info.is_vegetarian}, Vegan: {ingredient.nutritional_info.is_vegan}")
            print(f"Estimated Expiration Date: {ingredient.estimated_expiration_date}")
            print(f"Is Expired: {ingredient.is_expired()}")
            print(f"Estimated Financial Cost: EUR {ingredient.estimated_financial_cost:.2f}")