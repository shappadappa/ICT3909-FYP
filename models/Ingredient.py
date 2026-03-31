from models.NutritionalInformation import NutritionalInformation

from datetime import datetime

class Ingredient:
    def __init__(
            self,
            name: str, 
            grams_per_unit: float,
            nutritional_info: NutritionalInformation, 
            estimated_expiration_date: datetime = datetime(9999, 12, 31), 
            estimated_financial_cost: float = 0.0):
        """
        `Ingredient` class represents an ingredient in the pantry with various attributes useful for recipe suggestions and inventory management

        :param name: name of the ingredient
        :type name: str
        :param grams_per_unit: weight of one unit of the ingredient in grams
        :type grams_per_unit: float
        :param nutritional_info: nutritional information of the ingredient
        :type nutritional_info: NutritionalInformation
        :param estimated_expiration_date: estimated expiration date of the ingredient (default = datetime(9999, 12, 31), meaning it does not expire)
        :type estimated_expiration_date: datetime
        :param estimated_financial_cost: estimated financial cost of the ingredient per unit (default = 0.0)
        :type estimated_financial_cost: float
        """

        self.name = name
        self.grams_per_unit = grams_per_unit
        self.nutritional_info = nutritional_info
        self.estimated_expiration_date = estimated_expiration_date
        self.estimated_financial_cost = estimated_financial_cost

    def is_expired(self, current_date: datetime | None = None) -> bool:
        """
        Checks if the ingredient is expired based on the current date and the estimated expiration date

        :param current_date: current date to compare with the estimated expiration date (default = None, uses current system date)
        :type current_date: datetime | None

        :return: True if the ingredient is expired, False otherwise
        :rtype: bool
        """

        if self.estimated_expiration_date is None:
            return False

        if current_date is None:
            current_date = datetime.now()

        return current_date.timestamp() > self.estimated_expiration_date.timestamp()
    
    def nutrition_per_unit(self) -> NutritionalInformation:
        """
        Returns the nutritional information scaled to one unit of this ingredient
        (i.e. grams_per_unit / 100 × the per-100g values)

        :return: nutritional information for one unit of this ingredient
        :rtype: NutritionalInformation
        """

        scale = self.grams_per_unit / 100.0
        
        return NutritionalInformation(
            calories = self.nutritional_info.calories * scale,
            carbohydrates = self.nutritional_info.carbohydrates * scale,
            sugar = self.nutritional_info.sugar * scale,
            protein = self.nutritional_info.protein * scale,
            fat = self.nutritional_info.fat * scale,
            saturated_fat = self.nutritional_info.saturated_fat * scale,
            fiber = self.nutritional_info.fiber * scale,
            sodium = self.nutritional_info.sodium * scale,
            is_gluten_free = self.nutritional_info.is_gluten_free,
            is_lactose_free = self.nutritional_info.is_lactose_free,
            is_vegetarian = self.nutritional_info.is_vegetarian,
            is_vegan = self.nutritional_info.is_vegan,
        )

    def print(self):
        """
        Prints a summary of the ingredient's details
        """

        expiry_str = self.estimated_expiration_date.strftime('%Y-%m-%d') if self.estimated_expiration_date else 'N/A'

        print(
            f"Ingredient: {self.name}\n"
            f"\tGrams per Unit: {self.grams_per_unit} g\n"
            f"\tEstimated Expiration Date: {expiry_str}\n"
            f"\tEstimated Financial Cost per Unit: EUR {self.estimated_financial_cost:.2f}\n"
            f"\tNutritional Information:"
        )

        self.nutritional_info.print(2)